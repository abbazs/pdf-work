from pathlib import Path

import fitz

from cli.pdf.models import PasswordResult


def remove_pdf_password(input_path: str, output_path: str, password: str) -> PasswordResult:
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {input_path}")

    doc = fitz.open(src)
    was_encrypted = doc.is_encrypted

    if was_encrypted and not doc.authenticate(password):
        doc.close()
        raise ValueError(f"Failed to authenticate PDF with provided password: {input_path}")

    doc.save(dst)
    total_pages = len(doc)
    doc.close()

    return PasswordResult(
        input_path=str(src.resolve()),
        output_path=str(dst.resolve()),
        was_encrypted=was_encrypted,
        total_pages=total_pages,
    )
