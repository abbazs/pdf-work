from pathlib import Path

import fitz

from cli.pdf.models import MaskMatch, MaskResult

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
    name = color.strip().lower()
    if name in COLOR_MAP:
        return COLOR_MAP[name]
    if name.startswith("#") and len(name) == 7:
        h = name.lstrip("#")
        return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)
    msg = f"Invalid color: {color!r}. Use a name ({', '.join(COLOR_MAP)}) or hex (#RRGGBB)"
    raise ValueError(msg)


def mask_pdf_text(
    input_path: str,
    output_path: str,
    patterns: list[str],
    mask_line: bool = False,
    color: str = "black",
) -> MaskResult:
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {input_path}")

    fill = parse_color(color)
    matches: list[MaskMatch] = []
    total_redactions = 0
    pattern_found: dict[str, bool] = dict.fromkeys(patterns, False)

    doc = fitz.open(src)

    for page_num in range(len(doc)):
        page = doc[page_num]
        redacted_y_bands: set[tuple[float, float]] = set()

        for pattern in patterns:
            instances = page.search_for(pattern)
            if not instances:
                continue

            pattern_found[pattern] = True
            rects_to_redact: list[fitz.Rect] = []
            if mask_line:
                for match_rect in instances:
                    y0, y1 = match_rect.y0, match_rect.y1
                    band = (round(y0, 2), round(y1, 2))
                    if band in redacted_y_bands:
                        continue
                    redacted_y_bands.add(band)
                    rects_to_redact.append(fitz.Rect(0, y0, page.rect.width, y1))
            else:
                rects_to_redact = list(instances)

            for rect in rects_to_redact:
                page.add_redact_annot(rect, fill=fill)

            matches.append(
                MaskMatch(
                    page_number=page_num + 1,
                    pattern=pattern,
                    count=len(rects_to_redact),
                )
            )
            total_redactions += len(rects_to_redact)

        page.apply_redactions()

    for pattern in patterns:
        if not pattern_found[pattern]:
            matches.append(MaskMatch(page_number=0, pattern=pattern, count=0))

    doc.save(dst)
    doc.close()

    return MaskResult(
        input_path=str(src.resolve()),
        output_path=str(dst.resolve()),
        patterns=patterns,
        matches=matches,
        total_redactions=total_redactions,
    )
