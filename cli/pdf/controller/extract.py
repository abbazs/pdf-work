from pathlib import Path

import fitz

from cli.pdf.models import ExtractedPage, ExtractResult

# DPI levels to try when rasterizing to meet size limits (highest → lowest)
_RASTERIZE_DPIS = [300, 200, 150, 100, 72]


def extract_pages(
    input_path: str,
    pages: list[int],
    max_size: int | None = None,
) -> ExtractResult:
    src = Path(input_path)

    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {input_path}")

    doc = fitz.open(src)
    total_pages = len(doc)
    stem = src.stem
    parent_dir = src.parent

    extracted: list[ExtractedPage] = []
    skipped: list[int] = []

    for page_num in pages:
        if page_num < 1 or page_num > total_pages:
            skipped.append(page_num)
            continue

        # fitz uses 0-based indices
        zero_idx = page_num - 1
        out_path = parent_dir / f"{stem}-{page_num}.pdf"

        single = fitz.open()
        single.insert_pdf(doc, from_page=zero_idx, to_page=zero_idx)
        single.save(out_path)
        single.close()

        compressed = False

        if max_size is not None:
            file_size = out_path.stat().st_size
            if file_size > max_size:
                compressed = _compress_to_size(out_path, zero_idx, doc, max_size)

        final_size = out_path.stat().st_size

        extracted.append(
            ExtractedPage(
                page_number=page_num,
                output_path=str(out_path.resolve()),
                file_size=final_size,
                size_limit=max_size,
                compressed=compressed,
            )
        )

    doc.close()

    return ExtractResult(
        input_path=str(src.resolve()),
        total_pages=total_pages,
        extracted=extracted,
        skipped_pages=skipped,
    )


def _compress_to_size(
    out_path: Path,
    zero_idx: int,
    source_doc: fitz.Document,
    max_size: int,
) -> bool:
    """Attempt to compress an extracted page to fit within max_size bytes.

    Uses a best-result-wins strategy: tries multiple approaches and keeps
    whichever produces the smallest file, never making the output larger
    than the input. Returns True if compression was applied.
    """
    original_bytes = out_path.read_bytes()
    best_bytes = original_bytes

    # Level 1: re-save with garbage collection + deflate
    doc = fitz.open(out_path)
    level1_bytes = doc.tobytes(garbage=4, deflate=True, clean=True)
    doc.close()

    if len(level1_bytes) <= max_size:
        out_path.write_bytes(level1_bytes)
        return True

    if len(level1_bytes) < len(best_bytes):
        best_bytes = level1_bytes

    # Level 2: rasterize page as JPEG at progressively lower DPIs
    page = source_doc[zero_idx]
    for dpi in _RASTERIZE_DPIS:
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("jpg", jpg_quality=75)

        rasterized = fitz.open()
        new_page = rasterized.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=img_bytes)
        result_bytes = rasterized.tobytes(garbage=4, deflate=True, clean=True)
        rasterized.close()

        if len(result_bytes) <= max_size:
            out_path.write_bytes(result_bytes)
            return True

        if len(result_bytes) < len(best_bytes):
            best_bytes = result_bytes

    # Write whichever result was smallest (may still exceed the limit)
    out_path.write_bytes(best_bytes)
    return True
