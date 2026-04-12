from pathlib import Path

import fitz
import pytest


def _make_pdf(path: Path, text: str = "Hello World", pages: int = 1) -> None:
    doc = fitz.open()
    for _ in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), text, fontsize=12)
    doc.save(path)
    doc.close()


def _make_multi_pdf(path: Path, texts: list[str]) -> None:
    doc = fitz.open()
    for text in texts:
        page = doc.new_page()
        page.insert_text((72, 72), text, fontsize=12)
    doc.save(path)
    doc.close()


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "sample.pdf"
    _make_pdf(path, "Hello World")
    return path


@pytest.fixture
def multi_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "multi.pdf"
    _make_multi_pdf(path, ["Page One Content", "Page Two Stuff", "Page Three Things"])
    return path


@pytest.fixture
def two_pdfs(tmp_path: Path) -> list[Path]:
    paths = [tmp_path / "a.pdf", tmp_path / "b.pdf"]
    for p in paths:
        _make_pdf(p)
    return paths


def _make_pdf_with_metadata(
    path: Path,
    title: str = "Test Title",
    author: str = "Test Author",
    xmp: bool = False,
) -> None:
    """Create a PDF with Info dict metadata and optionally an XMP stream."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello", fontsize=12)
    doc.set_metadata({"title": title, "author": author, "producer": "pytest"})
    if xmp:
        # Minimal XMP that contains a dc:title entry
        xmp_xml = (
            '<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>'
            '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
            '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
            '<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">'
            f"<dc:title><rdf:Alt><rdf:li xml:lang=\"x-default\">{title}</rdf:li></rdf:Alt></dc:title>"
            "</rdf:Description></rdf:RDF></x:xmpmeta>"
            "<?xpacket end=\"w\"?>"
        )
        doc.set_xml_metadata(xmp_xml)
    doc.save(path)
    doc.close()


@pytest.fixture
def pdf_with_metadata(tmp_path: Path) -> Path:
    """PDF with Info dict metadata (title, author, producer) but no XMP stream."""
    path = tmp_path / "with_meta.pdf"
    _make_pdf_with_metadata(path, title="My Doc", author="Alice")
    return path


@pytest.fixture
def pdf_with_xmp(tmp_path: Path) -> Path:
    """PDF with both Info dict metadata and an XMP stream."""
    path = tmp_path / "with_xmp.pdf"
    _make_pdf_with_metadata(path, title="XMP Doc", author="Bob", xmp=True)
    return path
