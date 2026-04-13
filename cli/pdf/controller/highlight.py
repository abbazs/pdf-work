"""Controller for the highlight command — draws semi-transparent rectangles over matched text."""

from pathlib import Path

import fitz

from cli.pdf.models import HighlightMatch, HighlightResult

# Supported color names mapped to RGB tuples (components in 0.0–1.0 range)
COLOR_MAP: dict[str, tuple[float, float, float]] = {
    "black": (0, 0, 0),
    "white": (1, 1, 1),
    "red": (1, 0, 0),
    "green": (0, 1, 0),
    "blue": (0, 0, 1),
    "gray": (0.5, 0.5, 0.5),
    "grey": (0.5, 0.5, 0.5),
    "yellow": (1, 1, 0),
}


def parse_color(color: str) -> tuple[float, float, float]:
    """Parse a color name or #RRGGBB hex string into an RGB float tuple.

    Args:
        color: A color name from COLOR_MAP or a 7-character hex string like ``#FF8800``.

    Returns:
        A tuple of three floats in ``[0.0, 1.0]`` representing (R, G, B).

    Raises:
        ValueError: If the color is not a known name and not valid ``#RRGGBB`` hex.
    """
    name = color.strip().lower()
    if name in COLOR_MAP:
        return COLOR_MAP[name]
    if name.startswith("#") and len(name) == 7:
        h = name.lstrip("#")
        return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)
    msg = f"Invalid color: {color!r}. Use a name ({', '.join(COLOR_MAP)}) or hex (#RRGGBB)"
    raise ValueError(msg)


def highlight_pdf_text(
    input_path: str,
    output_path: str,
    patterns: list[str],
    mask_line: bool = False,
    color: str = "yellow",
    opacity: float = 0.4,
) -> HighlightResult:
    """Draw semi-transparent colored rectangles over matched text in a PDF.

    Unlike the mask command, the underlying text is *not* removed — it remains
    selectable and searchable in the output PDF.

    Args:
        input_path: Path to the source PDF file.
        output_path: Path where the annotated PDF will be saved.
        patterns: List of text strings to search for and highlight.
        mask_line: When True, expand each match to cover the full page width
            at the same vertical band (entire-line highlight).
        color: Fill color for the highlight rectangle. Accepts a name from
            ``COLOR_MAP`` or a ``#RRGGBB`` hex string. Defaults to ``"yellow"``.
        opacity: Transparency of the highlight (0.0 = invisible, 1.0 = opaque).
            Defaults to ``0.4``.

    Returns:
        A :class:`HighlightResult` summarising all matches and the output path.

    Raises:
        FileNotFoundError: If ``input_path`` does not exist.
        ValueError: If ``input_path`` is not a ``.pdf`` file, ``color`` is invalid,
            or ``opacity`` is outside ``[0.0, 1.0]``.
    """
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {input_path}")
    if not (0.0 <= opacity <= 1.0):
        raise ValueError(f"opacity must be between 0.0 and 1.0, got: {opacity}")

    fill = parse_color(color)
    matches: list[HighlightMatch] = []
    total_highlights = 0
    pattern_found: dict[str, bool] = dict.fromkeys(patterns, False)

    doc = fitz.open(src)

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Shared across ALL patterns for this page so that in line mode, a line
        # is highlighted at most once even when multiple patterns match it.
        highlighted_y_bands: set[tuple[float, float]] = set()

        for pattern in patterns:
            instances = page.search_for(pattern)
            if not instances:
                continue

            pattern_found[pattern] = True
            rects_to_draw: list[fitz.Rect] = []

            if mask_line:
                # Expand each match to full-width at the same y-band, deduplicating
                for match_rect in instances:
                    y0, y1 = match_rect.y0, match_rect.y1
                    band = (round(y0, 2), round(y1, 2))
                    if band in highlighted_y_bands:
                        continue
                    highlighted_y_bands.add(band)
                    rects_to_draw.append(fitz.Rect(0, y0, page.rect.width, y1))
            else:
                rects_to_draw = list(instances)

            for rect in rects_to_draw:
                # draw_rect with fill_opacity overlays the rectangle without
                # removing the underlying text content
                page.draw_rect(rect, color=None, fill=fill, fill_opacity=opacity, overlay=True)

            matches.append(
                HighlightMatch(
                    page_number=page_num + 1,
                    pattern=pattern,
                    count=len(rects_to_draw),
                )
            )
            total_highlights += len(rects_to_draw)

    # Record patterns that had no matches at all (page_number=0 sentinel)
    for pattern in patterns:
        if not pattern_found[pattern]:
            matches.append(HighlightMatch(page_number=0, pattern=pattern, count=0))

    doc.save(dst)
    doc.close()

    return HighlightResult(
        input_path=str(src.resolve()),
        output_path=str(dst.resolve()),
        patterns=patterns,
        matches=matches,
        total_highlights=total_highlights,
    )
