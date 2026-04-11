from pathlib import Path

import fitz

from cli.pdf.models import ReplaceMatch, ReplaceResult


def replace_pdf_text(
    input_path: str,
    output_path: str,
    pattern: str,
    replacement: str,
) -> ReplaceResult:
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {input_path}")

    doc = fitz.open(src)
    matches: list[ReplaceMatch] = []
    total_replacements = 0
    found_any = False

    for page_num in range(len(doc)):
        page = doc[page_num]
        instances = page.search_for(pattern)

        if not instances:
            continue

        found_any = True
        for rect in instances:
            page.add_redact_annot(rect, text=replacement, fontsize=11, fontname="helv")

        page.apply_redactions()

        count = len(instances)
        matches.append(
            ReplaceMatch(
                page_number=page_num + 1,
                pattern=pattern,
                replacement=replacement,
                count=count,
            )
        )
        total_replacements += count

    if not found_any:
        matches.append(
            ReplaceMatch(page_number=0, pattern=pattern, replacement=replacement, count=0)
        )

    doc.save(dst)
    doc.close()

    return ReplaceResult(
        input_path=str(src.resolve()),
        output_path=str(dst.resolve()),
        pattern=pattern,
        replacement=replacement,
        matches=matches,
        total_replacements=total_replacements,
    )
