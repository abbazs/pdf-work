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
