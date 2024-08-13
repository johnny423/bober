import re

from bober.src.parsing.line_parser import parse_line
from bober.src.parsing.parsed_types import ParsedLine, ParsedSection

# compile once for the whole program
PAGE_END_PATTERN = re.compile(r'(?:(?:\S+\s+)?\S+\s+)?\[Page \d+\]\s*$')


class SectionsParser:
    def __init__(self, doc: str):
        self.lines = doc.splitlines()
        self.current_section: dict[int, ParsedLine] = {}
        self.section_start_line: int | None = None
        self.current_page = 1
        self.current_line = 0
        self.line_in_page = 0

    def __iter__(self):
        return self

    def __next__(self) -> ParsedSection:
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line]
            self.current_line += 1
            self.line_in_page += 1

            if not line.strip():  # empty line
                if section := self._close_section():
                    return section
                continue

            if not self.current_section:  # new section
                self.section_start_line = self.line_in_page

            self.current_section[
                self.line_in_page - self.section_start_line
            ] = parse_line(line)

            # Check if this line is a page ending
            if PAGE_END_PATTERN.search(line):
                if section := self._close_section():
                    self.current_page += 1
                    self.line_in_page = 0
                    return section

        # End of document, yield last section if exists
        if section := self._close_section():
            return section

        raise StopIteration

    def _close_section(self) -> ParsedSection | None:
        if self.current_section:
            section = ParsedSection(
                page_line=self.section_start_line,
                lines=self.current_section,
                page=self.current_page,
            )
            # reset section info
            self.current_section = {}
            self.section_start_line = None
            return section

        return None
