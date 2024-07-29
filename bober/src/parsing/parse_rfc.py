from bober.src.parsing.parsed_types import ParsedDocument
from bober.src.parsing.sections_parser import SectionsParser


def parse_rfc(doc: str) -> ParsedDocument:
    sections = list(SectionsParser(doc))
    return ParsedDocument(sections=sections)
