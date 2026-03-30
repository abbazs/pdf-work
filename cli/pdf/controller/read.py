from pathlib import Path

import pdfplumber

from cli.pdf.models import PageText, PdfReadResult


def extract_pdf_text(file_path: str, pages: list[int] | None = None) -> PdfReadResult:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {file_path}")

    extracted_pages: list[PageText] = []
    total_chars = 0

    with pdfplumber.open(path) as pdf:
        total_pages = len(pdf.pages)
        page_indices = [p - 1 for p in pages] if pages else range(total_pages)

        for idx in page_indices:
            if idx < 0 or idx >= total_pages:
                continue

            page = pdf.pages[idx]
            text = (page.extract_text() or "").strip()

            extracted_pages.append(
                PageText(
                    page_number=idx + 1,
                    text=text,
                    char_count=len(text),
                    has_text=bool(text),
                )
            )
            total_chars += len(text)

    return PdfReadResult(
        file_path=str(path.resolve()),
        total_pages=total_pages,
        pages=extracted_pages,
        total_chars=total_chars,
    )
