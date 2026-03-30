from typing import Annotated

import cyclopts

from cli.pdf.controller.mask import mask_pdf_text
from cli.pdf.controller.read import extract_pdf_text
from cli.pdf.view.mask import show_mask_result
from cli.pdf.view.read import show_pdf_text
from cli.utils.decorators import cli_progress, handle_cli_errors

cli = cyclopts.App(name="pdf", help="PDF toolkit — read, mask, replace, and delete text")


@cli.command(name="read")
@handle_cli_errors
def read(
    file_path: Annotated[
        str, cyclopts.Parameter(name=["--file", "-f"], help="Path to the PDF file")
    ],
    pages: Annotated[
        list[int] | None,
        cyclopts.Parameter(
            name=["--pages", "-p"], help="Specific page numbers to extract (e.g. 1 3 5)"
        ),
    ] = None,
) -> None:
    """Read a PDF file and print its text content to the terminal."""
    with cli_progress("Extracting text from PDF..."):
        result = extract_pdf_text(file_path, pages=pages)

    show_pdf_text(result)


@cli.command(name="mask")
@handle_cli_errors
def mask(
    file_path: Annotated[
        str, cyclopts.Parameter(name=["--file", "-f"], help="Path to the input PDF file")
    ],
    output: Annotated[
        str, cyclopts.Parameter(name=["--output", "-o"], help="Path for the masked output PDF")
    ],
    text: Annotated[
        list[str],
        cyclopts.Parameter(
            name=["--text", "-t"],
            help="Text pattern to mask (repeatable, e.g. -t 'SSN' -t 'Account')",
        ),
    ],
    line: Annotated[
        bool,
        cyclopts.Parameter(
            name=["--line", "-l"],
            help="Mask the entire line containing matched text",
        ),
    ] = False,
    insensitive: Annotated[
        bool,
        cyclopts.Parameter(
            name=["--insensitive", "-i"],
            help="Case-insensitive text matching (search is case-insensitive by default)",
        ),
    ] = False,
    color: Annotated[
        str,
        cyclopts.Parameter(
            name=["--color", "-c"],
            help="Redaction fill color — name (black, white, gray, red) or hex (#RRGGBB)",
        ),
    ] = "black",
) -> None:
    """Mask specific text in a PDF by drawing colored rectangles over matches."""
    with cli_progress("Masking text in PDF..."):
        result = mask_pdf_text(file_path, output, patterns=text, mask_line=line, color=color)

    show_mask_result(result, mask_line=line, insensitive=insensitive, color=color)


if __name__ == "__main__":
    cli()
