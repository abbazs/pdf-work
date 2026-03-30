
import PyPDF2
import rich_click as click
from rich.pretty import pprint as print
from PyPDF2.generic import RectangleObject

def remove_pdf_password(input_pdf, output_pdf, password):
    """Remove password from a PDF file."""
    with open(input_pdf, "rb") as input_file:
        reader = PyPDF2.PdfReader(input_file)

        if reader.is_encrypted:
            reader.decrypt(password)

            writer = PyPDF2.PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            with open(output_pdf, "wb") as output_file:
                writer.write(output_file)

            print(f"Password removed. The file is saved as {output_pdf}.")
        else:
            print("The PDF file is not encrypted.")


def remove_last_page(input_pdf, output_pdf):
    """Remove the last page from a PDF file."""
    with open(input_pdf, "rb") as input_file:
        reader = PyPDF2.PdfReader(input_file)

        if len(reader.pages) <= 1:
            print("PDF has only one page or is empty. Cannot remove the last page.")
            return

        writer = PyPDF2.PdfWriter()

        # Add all pages except the last one
        for i in range(len(reader.pages) - 1):
            writer.add_page(reader.pages[i])

        with open(output_pdf, "wb") as output_file:
            writer.write(output_file)

        print(f"Last page removed. The file is saved as {output_pdf}.")
        print(
            f"Original pages: {len(reader.pages)}, New pages: {len(reader.pages) - 1}"
        )


def merge_pdfs(input_pdfs, output_pdf):
    """Merge multiple PDF files into one."""
    writer = PyPDF2.PdfWriter()
    total_pages = 0

    for pdf_path in input_pdfs:
        try:
            with open(pdf_path, "rb") as input_file:
                reader = PyPDF2.PdfReader(input_file)

                # Check if PDF is encrypted
                if reader.is_encrypted:
                    print(f"Warning: {pdf_path} is encrypted and will be skipped.")
                    print("Use the remove-password command first to decrypt it.")
                    continue

                page_count = len(reader.pages)
                print(f"Adding {page_count} pages from {pdf_path}")

                for page in reader.pages:
                    writer.add_page(page)

                total_pages += page_count

        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            continue

    if total_pages == 0:
        print("No pages to merge. Check your input files.")
        return

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

    print(f"Merged {len(input_pdfs)} files into {output_pdf}.")
    print(f"Total pages in merged file: {total_pages}")

def crop_pdf_height(input_pdf: str, output_pdf: str, height: float) -> None:
    """Crop each page of a PDF file to retain only the specified height from the top."""
    with open(input_pdf, "rb") as input_file:
        reader = PyPDF2.PdfReader(input_file)
        writer = PyPDF2.PdfWriter()

        for page in reader.pages:
            llx, lly = page.mediabox.lower_left
            urx, ury = page.mediabox.upper_right
            page_height = ury - lly

            if height > page_height:
                print(f"Requested height {height} exceeds page height {page_height}. Page left uncropped.")
                writer.add_page(page)
                continue

            new_lly = ury - height
            new_box = RectangleObject([llx, new_lly, urx, ury])
            page.mediabox = new_box
            page.cropbox = new_box
            writer.add_page(page)

        with open(output_pdf, "wb") as output_file:
            writer.write(output_file)

    print(f"Cropped PDF saved. Retained top height: {height}. File saved as {output_pdf}.")

@click.group()
def cli():
    """PDF utility tool with multiple commands."""
    pass


@cli.command()
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
@click.argument("password", type=str)
def remove_password(input_pdf, output_pdf, password):
    """Remove password from a PDF file and save it.

    Example:
        python script.py remove-password input.pdf output.pdf mypassword
    """
    remove_pdf_password(input_pdf, output_pdf, password)


@cli.command()
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
def remove_last_page_cmd(input_pdf, output_pdf):
    """Remove the last page from a PDF file.

    Example:
        python script.py remove-last-page input.pdf output.pdf
    """
    remove_last_page(input_pdf, output_pdf)


@cli.command()
@click.argument("output_pdf", type=click.Path())
@click.argument("input_pdfs", nargs=-1, required=True, type=click.Path(exists=True))
def merge(output_pdf, input_pdfs):
    """Merge multiple PDF files into one.

    Example:
        python script.py merge output.pdf file1.pdf file2.pdf file3.pdf
    """
    if len(input_pdfs) < 2:
        print("Error: At least 2 input PDF files are required for merging.")
        return

    merge_pdfs(input_pdfs, output_pdf)

@cli.command()
@click.argument("input_pdf", type=click.Path(exists=True))
@click.argument("output_pdf", type=click.Path())
@click.argument("height", type=float)
def crop(input_pdf, output_pdf, height):
    """Crop each page of a PDF file to retain only the specified height.

    Example:
        python script.py crop input.pdf output.pdf 500
    """
    crop_pdf_height(input_pdf, output_pdf, height)



if __name__ == "__main__":
    cli()
