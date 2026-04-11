from pathlib import Path

import fitz

from cli.pdf.models import PageRemoveResult


def remove_last_page(input_path: str, output_path: str) -> PageRemoveResult:
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {input_path}")

    doc = fitz.open(src)
    total = len(doc)

    if total <= 1:
        doc.close()
        raise ValueError(f"PDF has only {total} page(s). Cannot remove the last page.")

    removed_page = total
    doc.delete_page(total - 1)
    doc.save(dst)
    doc.close()

    return PageRemoveResult(
        input_path=str(src.resolve()),
        output_path=str(dst.resolve()),
        original_pages=total,
        new_pages=total - 1,
        removed_page=removed_page,
    )
