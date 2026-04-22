from dataclasses import dataclass, field


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str
    char_count: int
    has_text: bool


@dataclass(frozen=True)
class PdfReadResult:
    file_path: str
    total_pages: int
    pages: list[PageText] = field(default_factory=list)
    total_chars: int = 0

    @property
    def pages_with_text(self) -> int:
        return len([p for p in self.pages if p.has_text])

    @property
    def empty_pages(self) -> list[int]:
        return [p.page_number for p in self.pages if not p.has_text]


@dataclass(frozen=True)
class MaskMatch:
    page_number: int
    pattern: str
    count: int


@dataclass(frozen=True)
class MaskResult:
    input_path: str
    output_path: str
    patterns: list[str]
    matches: list[MaskMatch] = field(default_factory=list)
    total_redactions: int = 0

    @property
    def pages_affected(self) -> list[int]:
        return sorted({m.page_number for m in self.matches})

    @property
    def pages_with_matches(self) -> int:
        return len(self.pages_affected)


@dataclass(frozen=True)
class PasswordResult:
    input_path: str
    output_path: str
    was_encrypted: bool
    total_pages: int


@dataclass(frozen=True)
class PageRemoveResult:
    input_path: str
    output_path: str
    original_pages: int
    new_pages: int
    removed_page: int


@dataclass(frozen=True)
class MergeResult:
    output_path: str
    input_files: list[str]
    total_pages: int
    skipped_files: list[str]


@dataclass(frozen=True)
class CropResult:
    input_path: str
    output_path: str
    height: float
    total_pages: int
    pages_cropped: int
    pages_skipped: int


@dataclass(frozen=True)
class ReplaceMatch:
    page_number: int
    pattern: str
    replacement: str
    count: int


@dataclass(frozen=True)
class ReplaceResult:
    input_path: str
    output_path: str
    pattern: str
    replacement: str
    matches: list[ReplaceMatch] = field(default_factory=list)
    total_replacements: int = 0

    @property
    def pages_affected(self) -> list[int]:
        return sorted({m.page_number for m in self.matches})

    @property
    def pages_with_matches(self) -> int:
        return len(self.pages_affected)


@dataclass(frozen=True)
class DeleteMatch:
    page_number: int
    pattern: str
    count: int


@dataclass(frozen=True)
class DeleteResult:
    input_path: str
    output_path: str
    patterns: list[str]
    matches: list[DeleteMatch] = field(default_factory=list)
    total_deletions: int = 0

    @property
    def pages_affected(self) -> list[int]:
        return sorted({m.page_number for m in self.matches})

    @property
    def pages_with_matches(self) -> int:
        return len(self.pages_affected)


@dataclass(frozen=True)
class MetadataResult:
    """Result of stripping metadata from a PDF."""

    input_path: str
    output_path: str
    total_pages: int
    # Metadata keys that had non-empty values before removal
    fields_cleared: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class HighlightMatch:
    """A single pattern match found during highlighting."""

    page_number: int
    pattern: str
    count: int


@dataclass(frozen=True)
class HighlightResult:
    """Result of highlighting text in a PDF."""

    input_path: str
    output_path: str
    patterns: list[str]
    matches: list[HighlightMatch] = field(default_factory=list)
    total_highlights: int = 0

    @property
    def pages_affected(self) -> list[int]:
        """Sorted list of page numbers that had at least one highlight."""
        return sorted({m.page_number for m in self.matches if m.page_number > 0})

    @property
    def pages_with_matches(self) -> int:
        """Number of pages that had at least one highlight."""
        return len(self.pages_affected)


@dataclass(frozen=True)
class ExtractedPage:
    """A single page extracted as a separate PDF file."""

    page_number: int
    output_path: str
    file_size: int
    size_limit: int | None = None
    compressed: bool = False


@dataclass(frozen=True)
class ExtractResult:
    """Result of extracting individual pages from a PDF."""

    input_path: str
    total_pages: int
    extracted: list[ExtractedPage] = field(default_factory=list)
    skipped_pages: list[int] = field(default_factory=list)

    @property
    def pages_extracted(self) -> int:
        """Number of pages successfully extracted."""
        return len(self.extracted)
