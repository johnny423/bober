import pytest

from bober.src.parsing.parsed_types import ParsedSection
from bober.src.parsing.sections_parser import SectionsParser


class TestSectionsParser:

    def test_single_section(self) -> None:
        doc = "This is a single section\nwith multiple lines"
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 1
        assert sections[0].page_line == 1
        assert len(sections[0].lines) == 2

    def test_multiple_sections(self) -> None:
        doc = "Section 1\nLine 2\n\nSection 2\nLine 2"
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 2
        assert sections[0].page_line == 1
        assert sections[1].page_line == 4

    def test_empty_document(self) -> None:
        doc = ""
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 0

    def test_document_with_only_empty_lines(self) -> None:
        doc = "\n\n\n"
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 0

    def test_sections_with_page_breaks(self) -> None:
        doc = "Section 1\nLine 2 [Page 1]\nSection 2\nLine 2 [Page 2]"
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 2
        assert sections[0].lines[1].text.endswith("[Page 1]")
        assert sections[1].lines[1].text.endswith("[Page 2]")
        assert sections[0].page == 1
        assert sections[1].page == 2

    def test_sections_with_multiple_page_breaks(self) -> None:
        doc = "Section 1\nLine 2 [Page 1]\nSection 2\nLine 2 [Page 2]\nSection 3\nLine 2 [Page 3]"
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 3
        assert sections[0].page == 1
        assert sections[1].page == 2
        assert sections[2].page == 3

    def test_section_with_empty_lines_within(self) -> None:
        doc = "Section 1\nLine 2\n\nLine 3\nLine 4"
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 2
        assert len(sections[0].lines) == 2
        assert len(sections[1].lines) == 2

    def test_section_with_indentation(self) -> None:
        doc = "Section 1\n  Indented line\nNormal line"
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 1
        assert sections[0].lines[1].indentation == 2

    def test_section_with_special_characters(self) -> None:
        doc = "Section 1\nLine with @#$%^&*\nNormal line"
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 1
        assert "@#$%^&*" in sections[0].lines[1].text

    def test_section_with_numbers(self) -> None:
        doc = "Section 1\nLine with 12345\nNormal line"
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 1
        assert "12345" in sections[0].lines[1].text

    def test_complex_document(self) -> None:
        doc = """Section 1
Line 2
Line 3 [Page 1]

Section 2
  Indented line
Normal line

Section 3
Line with @#$%^&*
Line with 12345 [Page 2]"""
        parser = SectionsParser(doc)
        sections = list(parser)
        assert len(sections) == 3

        assert sections[0].lines[2].text.endswith("[Page 1]")
        assert sections[0].page == 1

        assert sections[1].lines[1].indentation == 2
        assert sections[1].page == 2

        assert "@#$%^&*" in sections[2].lines[1].text
        assert sections[2].lines[2].text.endswith("[Page 2]")
        assert sections[2].page == 2

    def test_iterator_behavior(self) -> None:
        doc = "Section 1\nLine 2\n\nSection 2\nLine 2"
        parser = SectionsParser(doc)
        iterator = iter(parser)
        assert isinstance(next(iterator), ParsedSection)
        assert isinstance(next(iterator), ParsedSection)
        with pytest.raises(StopIteration):
            next(iterator)
