from pathlib import Path

import fitz

from cli.pdf.models import CropResult


def crop_pdf(input_path: str, output_path: str, height: float) -> CropResult:
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {input_path}")
    if height <= 0:
        raise ValueError(f"Crop height must be positive, got {height}")

    doc = fitz.open(src)
    total_pages = len(doc)
    pages_cropped = 0
    pages_skipped = 0

    for page_num in range(total_pages):
        page = doc[page_num]
        ury = page.rect.height
        if height > ury:
            pages_skipped += 1
            continue

        rect = fitz.Rect(0, ury - height, page.rect.width, ury)
        page.set_cropbox(rect)
        page.set_mediabox(rect)
        pages_cropped += 1

    doc.save(dst)
    doc.close()

    return CropResult(
        input_path=str(src.resolve()),
        output_path=str(dst.resolve()),
        height=height,
        total_pages=total_pages,
        pages_cropped=pages_cropped,
        pages_skipped=pages_skipped,
    )
