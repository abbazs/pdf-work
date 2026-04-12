import os
import shutil
import tempfile
from pathlib import Path

import fitz

from cli.pdf.models import MetadataResult

# All metadata keys exposed by PyMuPDF
_METADATA_KEYS: tuple[str, ...] = (
    "title", "author", "subject", "keywords",
    "creator", "producer", "creationDate", "modDate",
)


def remove_pdf_metadata(input_path: str, output_path: str) -> MetadataResult:
    """Strip all metadata fields from a PDF and save the cleaned file.

    Supports in-place operation (input and output may be the same path):
    the file is written to a temporary location first, then replaced atomically.
    """
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    if src.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {input_path}")

    # When saving to the same path, PyMuPDF requires incremental save mode
    # which cannot clear metadata. Write to a sibling temp file, then replace.
    in_place = src.resolve() == dst.resolve()

    doc = fitz.open(src)
    try:
        total_pages = len(doc)

        # Capture which fields were non-empty before clearing (Info dict)
        existing_meta = doc.metadata or {}
        fields_cleared = [key for key in _METADATA_KEYS if existing_meta.get(key)]
        # Also note if an XMP stream was present
        if doc.get_xml_metadata():
            fields_cleared.append("xmp")

        # Wipe Info dictionary metadata (classic PDF metadata)
        doc.set_metadata({})
        # Wipe XMP metadata stream (modern embedded XML metadata — contains title,
        # author, creator tool, dates, etc. even after the Info dict is cleared)
        doc.del_xml_metadata()

        if in_place:
            tmp_fd, tmp_path_str = tempfile.mkstemp(dir=src.parent, suffix=".pdf")
            os.close(tmp_fd)  # fitz opens the path by name; close the raw fd first
            tmp_path = Path(tmp_path_str)
            try:
                doc.save(tmp_path_str)
                shutil.move(tmp_path_str, src)
            except Exception:
                tmp_path.unlink(missing_ok=True)
                raise
        else:
            doc.save(dst)

        # Construct result inside try so all local variables are guaranteed bound
        return MetadataResult(
            input_path=str(src.resolve()),
            output_path=str(dst.resolve()),
            total_pages=total_pages,
            fields_cleared=fields_cleared,
        )
    finally:
        doc.close()
