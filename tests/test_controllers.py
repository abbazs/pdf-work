from pathlib import Path

import fitz
import pytest

from cli.pdf.controller.crop import crop_pdf
from cli.pdf.controller.delete import delete_pdf_text
from cli.pdf.controller.mask import mask_pdf_text, parse_color
from cli.pdf.controller.merge import merge_pdfs
from cli.pdf.controller.read import extract_pdf_text
from cli.pdf.controller.remove_last_page import remove_last_page
from cli.pdf.controller.remove_password import remove_pdf_password
from cli.pdf.controller.replace import replace_pdf_text


class TestParseColor:
    def test_valid_name_black(self):
        assert parse_color("black") == (0, 0, 0)

    def test_valid_name_white(self):
        assert parse_color("white") == (1, 1, 1)

    def test_valid_name_red(self):
        assert parse_color("red") == (1, 0, 0)

    def test_valid_name_green(self):
        assert parse_color("green") == (0, 1, 0)

    def test_valid_name_blue(self):
        assert parse_color("blue") == (0, 0, 1)

    def test_valid_name_gray(self):
        assert parse_color("gray") == (0.5, 0.5, 0.5)

    def test_valid_name_grey(self):
        assert parse_color("grey") == (0.5, 0.5, 0.5)

    def test_valid_name_yellow(self):
        assert parse_color("yellow") == (1, 1, 0)

    def test_case_insensitive(self):
        assert parse_color("BLACK") == (0, 0, 0)

    def test_whitespace_trimmed(self):
        assert parse_color("  black  ") == (0, 0, 0)

    def test_valid_hex_full_white(self):
        assert parse_color("#FFFFFF") == (1.0, 1.0, 1.0)

    def test_valid_hex_custom(self):
        assert parse_color("#808080") == (128 / 255, 128 / 255, 128 / 255)

    def test_invalid_color_raises(self):
        with pytest.raises(ValueError, match="Invalid color"):
            parse_color("not_a_color")

    def test_invalid_hex_short_raises(self):
        with pytest.raises(ValueError, match="Invalid color"):
            parse_color("#FF")

    def test_invalid_hex_long_raises(self):
        with pytest.raises(ValueError, match="Invalid color"):
            parse_color("#FFAABBCC")


class TestExtractPdfText:
    def test_reads_single_page(self, sample_pdf: Path):
        result = extract_pdf_text(str(sample_pdf))
        assert result.total_pages == 1
        assert len(result.pages) == 1
        assert "Hello" in result.pages[0].text
        assert result.total_chars > 0

    def test_reads_all_pages_multi(self, multi_pdf: Path):
        result = extract_pdf_text(str(multi_pdf))
        assert result.total_pages == 3
        assert len(result.pages) == 3

    def test_reads_specific_pages(self, multi_pdf: Path):
        result = extract_pdf_text(str(multi_pdf), pages=[1, 3])
        assert len(result.pages) == 2
        assert result.pages[0].page_number == 1
        assert result.pages[1].page_number == 3

    def test_reads_single_page_number(self, multi_pdf: Path):
        result = extract_pdf_text(str(multi_pdf), pages=[2])
        assert len(result.pages) == 1
        assert result.pages[0].page_number == 2
        assert "Two" in result.pages[0].text

    def test_out_of_range_page_skipped(self, multi_pdf: Path):
        result = extract_pdf_text(str(multi_pdf), pages=[99])
        assert len(result.pages) == 0
        assert result.total_pages == 3

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract_pdf_text("/nonexistent/file.pdf")

    def test_non_pdf_raises(self, tmp_path: Path):
        txt = tmp_path / "test.txt"
        txt.write_text("not a pdf")
        with pytest.raises(ValueError, match="Not a PDF"):
            extract_pdf_text(str(txt))


class TestMaskPdfText:
    def test_masks_text_creates_output(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "masked.pdf"
        result = mask_pdf_text(str(sample_pdf), str(out), ["Hello"])
        assert out.exists()
        assert result.total_redactions > 0
        assert len(result.matches) >= 1

    def test_output_has_same_page_count(self, multi_pdf: Path, tmp_path: Path):
        out = tmp_path / "masked.pdf"
        result = mask_pdf_text(str(multi_pdf), str(out), ["Page"])
        doc = fitz.open(out)
        assert len(doc) == 3
        doc.close()
        assert result.total_redactions > 0

    def test_multiple_patterns(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "masked.pdf"
        result = mask_pdf_text(str(sample_pdf), str(out), ["Hello", "World"])
        assert result.total_redactions >= 2

    def test_line_mode(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "masked.pdf"
        result = mask_pdf_text(str(sample_pdf), str(out), ["Hello"], mask_line=True)
        assert result.total_redactions > 0

    def test_no_match_still_creates_output(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "masked.pdf"
        result = mask_pdf_text(str(sample_pdf), str(out), ["ZZZZNOTFOUND"])
        assert out.exists()
        assert result.total_redactions == 0

    def test_file_not_found(self, tmp_path: Path):
        out = tmp_path / "out.pdf"
        with pytest.raises(FileNotFoundError):
            mask_pdf_text("/nonexistent/file.pdf", str(out), ["x"])

    def test_non_pdf_raises(self, tmp_path: Path):
        txt = tmp_path / "test.txt"
        txt.write_text("not a pdf")
        out = tmp_path / "out.pdf"
        with pytest.raises(ValueError, match="Not a PDF"):
            mask_pdf_text(str(txt), str(out), ["x"])


class TestReplacePdfText:
    def test_replaces_text(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "replaced.pdf"
        result = replace_pdf_text(str(sample_pdf), str(out), "Hello", "Goodbye")
        assert out.exists()
        assert result.total_replacements > 0

    def test_correct_match_count(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "replaced.pdf"
        result = replace_pdf_text(str(sample_pdf), str(out), "Hello", "X")
        assert result.total_replacements == 1
        assert len(result.matches) == 1
        assert result.matches[0].count == 1

    def test_no_match_returns_zero(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "replaced.pdf"
        result = replace_pdf_text(str(sample_pdf), str(out), "ZZZZZ", "X")
        assert out.exists()
        assert result.total_replacements == 0
        assert len(result.matches) == 1
        assert result.matches[0].count == 0

    def test_file_not_found(self, tmp_path: Path):
        out = tmp_path / "out.pdf"
        with pytest.raises(FileNotFoundError):
            replace_pdf_text("/nonexistent/file.pdf", str(out), "a", "b")

    def test_non_pdf_raises(self, tmp_path: Path):
        txt = tmp_path / "test.txt"
        txt.write_text("not a pdf")
        out = tmp_path / "out.pdf"
        with pytest.raises(ValueError, match="Not a PDF"):
            replace_pdf_text(str(txt), str(out), "a", "b")


class TestDeletePdfText:
    def test_deletes_text(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "deleted.pdf"
        result = delete_pdf_text(str(sample_pdf), str(out), ["Hello"])
        assert out.exists()
        assert result.total_deletions > 0

    def test_correct_deletion_count(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "deleted.pdf"
        result = delete_pdf_text(str(sample_pdf), str(out), ["Hello"])
        assert result.total_deletions == 1
        assert result.matches[0].count == 1

    def test_no_match_returns_zero(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "deleted.pdf"
        result = delete_pdf_text(str(sample_pdf), str(out), ["ZZZZZ"])
        assert out.exists()
        assert result.total_deletions == 0

    def test_multiple_patterns(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "deleted.pdf"
        result = delete_pdf_text(str(sample_pdf), str(out), ["Hello", "World"])
        assert result.total_deletions >= 2

    def test_file_not_found(self, tmp_path: Path):
        out = tmp_path / "out.pdf"
        with pytest.raises(FileNotFoundError):
            delete_pdf_text("/nonexistent/file.pdf", str(out), ["x"])

    def test_non_pdf_raises(self, tmp_path: Path):
        txt = tmp_path / "test.txt"
        txt.write_text("not a pdf")
        out = tmp_path / "out.pdf"
        with pytest.raises(ValueError, match="Not a PDF"):
            delete_pdf_text(str(txt), str(out), ["x"])


class TestRemovePdfPassword:
    def test_copies_unencrypted_pdf(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "unlocked.pdf"
        result = remove_pdf_password(str(sample_pdf), str(out), "unused")
        assert out.exists()
        assert result.was_encrypted is False
        assert result.total_pages == 1

    def test_output_is_valid_pdf(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "unlocked.pdf"
        remove_pdf_password(str(sample_pdf), str(out), "unused")
        doc = fitz.open(out)
        assert len(doc) == 1
        doc.close()

    def test_file_not_found(self, tmp_path: Path):
        out = tmp_path / "out.pdf"
        with pytest.raises(FileNotFoundError):
            remove_pdf_password("/nonexistent/file.pdf", str(out), "pass")

    def test_non_pdf_raises(self, tmp_path: Path):
        txt = tmp_path / "test.txt"
        txt.write_text("not a pdf")
        out = tmp_path / "out.pdf"
        with pytest.raises(ValueError, match="Not a PDF"):
            remove_pdf_password(str(txt), str(out), "pass")


class TestRemoveLastPage:
    def test_removes_last_page(self, multi_pdf: Path, tmp_path: Path):
        out = tmp_path / "trimmed.pdf"
        result = remove_last_page(str(multi_pdf), str(out))
        assert out.exists()
        assert result.original_pages == 3
        assert result.new_pages == 2
        assert result.removed_page == 3

    def test_output_page_count(self, multi_pdf: Path, tmp_path: Path):
        out = tmp_path / "trimmed.pdf"
        remove_last_page(str(multi_pdf), str(out))
        doc = fitz.open(out)
        assert len(doc) == 2
        doc.close()

    def test_single_page_raises(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "trimmed.pdf"
        with pytest.raises(ValueError, match="Cannot remove the last page"):
            remove_last_page(str(sample_pdf), str(out))

    def test_file_not_found(self, tmp_path: Path):
        out = tmp_path / "out.pdf"
        with pytest.raises(FileNotFoundError):
            remove_last_page("/nonexistent/file.pdf", str(out))

    def test_non_pdf_raises(self, tmp_path: Path):
        txt = tmp_path / "test.txt"
        txt.write_text("not a pdf")
        out = tmp_path / "out.pdf"
        with pytest.raises(ValueError, match="Not a PDF"):
            remove_last_page(str(txt), str(out))


class TestMergePdfs:
    def test_merges_two_pdfs(self, two_pdfs: list[Path], tmp_path: Path):
        out = tmp_path / "merged.pdf"
        files = [str(p) for p in two_pdfs]
        result = merge_pdfs(files, str(out))
        assert out.exists()
        assert result.total_pages == 2
        assert len(result.input_files) == 2

    def test_output_page_count(self, two_pdfs: list[Path], tmp_path: Path):
        out = tmp_path / "merged.pdf"
        files = [str(p) for p in two_pdfs]
        merge_pdfs(files, str(out))
        doc = fitz.open(out)
        assert len(doc) == 2
        doc.close()

    def test_single_file_raises(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "merged.pdf"
        with pytest.raises(ValueError, match="At least 2"):
            merge_pdfs([str(sample_pdf)], str(out))

    def test_empty_list_raises(self, tmp_path: Path):
        out = tmp_path / "merged.pdf"
        with pytest.raises(ValueError, match="At least 2"):
            merge_pdfs([], str(out))

    def test_skips_nonexistent_files(self, two_pdfs: list[Path], tmp_path: Path):
        out = tmp_path / "merged.pdf"
        files = [str(two_pdfs[0]), "/nonexistent/file.pdf", str(two_pdfs[1])]
        result = merge_pdfs(files, str(out))
        assert out.exists()
        assert result.total_pages == 2
        assert "/nonexistent/file.pdf" in result.skipped_files

    def test_skips_non_pdf_files(self, two_pdfs: list[Path], tmp_path: Path):
        out = tmp_path / "merged.pdf"
        txt = tmp_path / "test.txt"
        txt.write_text("not a pdf")
        files = [str(two_pdfs[0]), str(txt), str(two_pdfs[1])]
        result = merge_pdfs(files, str(out))
        assert out.exists()
        assert result.total_pages == 2
        assert str(txt) in result.skipped_files

    def test_fewer_than_2_valid_after_filtering_raises(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "merged.pdf"
        with pytest.raises(ValueError, match="Only 1 valid"):
            merge_pdfs([str(sample_pdf), "/nonexistent/file.pdf"], str(out))


class TestCropPdf:
    def test_crops_pdf(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "cropped.pdf"
        result = crop_pdf(str(sample_pdf), str(out), 200.0)
        assert out.exists()
        assert result.pages_cropped == 1
        assert result.pages_skipped == 0

    def test_output_is_valid(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "cropped.pdf"
        crop_pdf(str(sample_pdf), str(out), 200.0)
        doc = fitz.open(out)
        assert len(doc) == 1
        doc.close()

    def test_height_zero_raises(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "cropped.pdf"
        with pytest.raises(ValueError, match="must be positive"):
            crop_pdf(str(sample_pdf), str(out), 0)

    def test_height_negative_raises(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "cropped.pdf"
        with pytest.raises(ValueError, match="must be positive"):
            crop_pdf(str(sample_pdf), str(out), -50.0)

    def test_height_greater_than_page_height_skips(self, sample_pdf: Path, tmp_path: Path):
        out = tmp_path / "cropped.pdf"
        result = crop_pdf(str(sample_pdf), str(out), 99999.0)
        assert out.exists()
        assert result.pages_cropped == 0
        assert result.pages_skipped == 1

    def test_file_not_found(self, tmp_path: Path):
        out = tmp_path / "cropped.pdf"
        with pytest.raises(FileNotFoundError):
            crop_pdf("/nonexistent/file.pdf", str(out), 200.0)

    def test_non_pdf_raises(self, tmp_path: Path):
        txt = tmp_path / "test.txt"
        txt.write_text("not a pdf")
        out = tmp_path / "cropped.pdf"
        with pytest.raises(ValueError, match="Not a PDF"):
            crop_pdf(str(txt), str(out), 200.0)

    def test_crops_multi_page(self, multi_pdf: Path, tmp_path: Path):
        out = tmp_path / "cropped.pdf"
        result = crop_pdf(str(multi_pdf), str(out), 200.0)
        assert out.exists()
        assert result.total_pages == 3
        assert result.pages_cropped == 3
