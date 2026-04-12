from typing import Annotated

import cyclopts

from cli.pdf.controller.crop import crop_pdf
from cli.pdf.controller.delete import delete_pdf_text
from cli.pdf.controller.mask import mask_pdf_text
from cli.pdf.controller.merge import merge_pdfs
from cli.pdf.controller.read import extract_pdf_text
from cli.pdf.controller.remove_last_page import remove_last_page as _remove_last_page_ctrl
from cli.pdf.controller.remove_metadata import remove_pdf_metadata
from cli.pdf.controller.remove_password import remove_pdf_password
from cli.pdf.controller.replace import replace_pdf_text
from cli.pdf.view.crop import show_crop_result
from cli.pdf.view.delete import show_delete_result
from cli.pdf.view.mask import show_mask_result
from cli.pdf.view.merge import show_merge_result
from cli.pdf.view.read import show_pdf_text
from cli.pdf.view.remove_last_page import show_remove_result
from cli.pdf.view.remove_metadata import show_metadata_result
from cli.pdf.view.remove_password import show_password_result
from cli.pdf.view.replace import show_replace_result
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


@cli.command(name="replace")
@handle_cli_errors
def replace(
    file_path: Annotated[
        str, cyclopts.Parameter(name=["--file", "-f"], help="Path to the input PDF file")
    ],
    output: Annotated[
        str, cyclopts.Parameter(name=["--output", "-o"], help="Path for the output PDF")
    ],
    text: Annotated[
        str,
        cyclopts.Parameter(name=["--text", "-t"], help="Text pattern to find"),
    ],
    with_text: Annotated[
        str,
        cyclopts.Parameter(name=["--with", "-w"], help="Replacement text"),
    ],
) -> None:
    """Find and replace text in a PDF with new text."""
    with cli_progress("Replacing text in PDF..."):
        result = replace_pdf_text(file_path, output, pattern=text, replacement=with_text)

    show_replace_result(result)


@cli.command(name="delete")
@handle_cli_errors
def delete(
    file_path: Annotated[
        str, cyclopts.Parameter(name=["--file", "-f"], help="Path to the input PDF file")
    ],
    output: Annotated[
        str, cyclopts.Parameter(name=["--output", "-o"], help="Path for the output PDF")
    ],
    text: Annotated[
        list[str],
        cyclopts.Parameter(
            name=["--text", "-t"],
            help="Text pattern to delete (repeatable, e.g. -t 'SSN' -t 'Account')",
        ),
    ],
) -> None:
    """Find and permanently remove text from a PDF."""
    with cli_progress("Deleting text from PDF..."):
        result = delete_pdf_text(file_path, output, patterns=text)

    show_delete_result(result)


@cli.command(name="remove-password")
@handle_cli_errors
def remove_password(
    file_path: Annotated[
        str, cyclopts.Parameter(name=["--file", "-f"], help="Path to the encrypted PDF file")
    ],
    output: Annotated[
        str, cyclopts.Parameter(name=["--output", "-o"], help="Path for the decrypted output PDF")
    ],
    password: Annotated[
        str,
        cyclopts.Parameter(
            name=["--password"],
            help="Password to decrypt the PDF (visible in shell history)",
        ),
    ],
) -> None:
    """Remove password protection from a PDF file."""
    with cli_progress("Removing password from PDF..."):
        result = remove_pdf_password(file_path, output, password=password)

    show_password_result(result)


@cli.command(name="remove-last-page")
@handle_cli_errors
def remove_last_page(
    file_path: Annotated[
        str, cyclopts.Parameter(name=["--file", "-f"], help="Path to the PDF file")
    ],
    output: Annotated[
        str, cyclopts.Parameter(name=["--output", "-o"], help="Path for the output PDF")
    ],
) -> None:
    """Remove the last page from a PDF file."""
    with cli_progress("Removing last page from PDF..."):
        result = _remove_last_page_ctrl(file_path, output)

    show_remove_result(result)


@cli.command(name="remove-metadata")
@handle_cli_errors
def remove_metadata(
    file_path: Annotated[
        str, cyclopts.Parameter(name=["--file", "-f"], help="Path to the input PDF file")
    ],
    output: Annotated[
        str, cyclopts.Parameter(name=["--output", "-o"], help="Path for the cleaned output PDF")
    ],
) -> None:
    """Strip all metadata (author, title, dates, etc.) from a PDF file."""
    with cli_progress("Removing metadata from PDF..."):
        result = remove_pdf_metadata(file_path, output)

    show_metadata_result(result)


@cli.command(name="merge")
@handle_cli_errors
def merge(
    output: Annotated[
        str, cyclopts.Parameter(name=["--output", "-o"], help="Path for the merged output PDF")
    ],
    files: Annotated[
        list[str],
        cyclopts.Parameter(name=["--files"], help="PDF files to merge (repeatable)"),
    ],
) -> None:
    """Merge multiple PDF files into a single PDF."""
    with cli_progress("Merging PDF files..."):
        result = merge_pdfs(files, output)

    show_merge_result(result)


@cli.command(name="crop")
@handle_cli_errors
def crop(
    file_path: Annotated[
        str, cyclopts.Parameter(name=["--file", "-f"], help="Path to the PDF file")
    ],
    output: Annotated[
        str, cyclopts.Parameter(name=["--output", "-o"], help="Path for the cropped output PDF")
    ],
    height: Annotated[
        float,
        cyclopts.Parameter(
            name=["--height", "-h"], help="Crop height in points (from top of page)"
        ),
    ],
) -> None:
    """Crop all pages of a PDF to a specific height from the top."""
    with cli_progress("Cropping PDF pages..."):
        result = crop_pdf(file_path, output, height=height)

    show_crop_result(result)


if __name__ == "__main__":
    cli()
