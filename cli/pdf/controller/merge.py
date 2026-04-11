from pathlib import Path

import fitz

from cli.pdf.models import MergeResult


def merge_pdfs(input_files: list[str], output_path: str) -> MergeResult:
    dst = Path(output_path)

    if len(input_files) < 2:
        raise ValueError("At least 2 PDF files are required to merge.")

    valid_files: list[str] = []
    skipped_files: list[str] = []

    for f in input_files:
        p = Path(f)
        if not p.exists():
            skipped_files.append(f)
            continue
        if p.suffix.lower() != ".pdf":
            skipped_files.append(f)
            continue
        valid_files.append(f)

    if len(valid_files) < 2:
        raise ValueError(
            f"Only {len(valid_files)} valid PDF file(s) found. At least 2 are required."
        )

    merged = fitz.open()
    total_pages = 0

    for f in valid_files:
        try:
            src = fitz.open(f)
            merged.insert_pdf(src)
            total_pages += len(src)
            src.close()
        except Exception:
            skipped_files.append(f)

    merged.save(dst)
    merged.close()

    return MergeResult(
        output_path=str(dst.resolve()),
        input_files=valid_files,
        total_pages=total_pages,
        skipped_files=skipped_files,
    )
