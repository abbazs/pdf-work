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
