from dataclasses import dataclass


@dataclass
class AbsPosition:
    line: int
    column: int
    length: int

    def __str__(self) -> str:
        return f"Line {self.line} column {self.column} length: {self.length}"


@dataclass
class RelativePosition:
    section: int
    line: int
    word: int

    def __str__(self) -> str:
        return f"Section {self.section} line {self.line} word: {self.word}"


# todo: do we need it?
@dataclass
class PagePosition:
    page: int
    line: int
    column: int
