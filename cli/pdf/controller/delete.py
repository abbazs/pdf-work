from pathlib import Path

import fitz

from cli.pdf.models import DeleteMatch, DeleteResult


def delete_pdf_text(
    input_path: str,
    output_path: str,
    patterns: list[str],
) -> DeleteResult:
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {input_path}")

    doc = fitz.open(src)
    matches: list[DeleteMatch] = []
    total_deletions = 0
    pattern_found: dict[str, bool] = dict.fromkeys(patterns, False)

    for page_num in range(len(doc)):
        page = doc[page_num]

        for pattern in patterns:
            instances = page.search_for(pattern)

            if not instances:
                continue

            pattern_found[pattern] = True
            for rect in instances:
                page.add_redact_annot(rect, fill=(1, 1, 1))

            matches.append(
                DeleteMatch(
                    page_number=page_num + 1,
                    pattern=pattern,
                    count=len(instances),
                )
            )
            total_deletions += len(instances)

        page.apply_redactions()

    for pattern in patterns:
        if not pattern_found[pattern]:
            matches.append(DeleteMatch(page_number=0, pattern=pattern, count=0))

    doc.save(dst)
    doc.close()

    return DeleteResult(
        input_path=str(src.resolve()),
        output_path=str(dst.resolve()),
        patterns=patterns,
        matches=matches,
        total_deletions=total_deletions,
    )
