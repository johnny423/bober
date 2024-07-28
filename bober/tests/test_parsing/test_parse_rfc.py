from pathlib import Path

from bober.src.parsing.parse_rfc import parse_rfc
from bober.src.parsing.parsed_types import ParsedDocument

CURR_DIR = Path(__file__).parent
DOC_TO_TEST = CURR_DIR.parent.parent / "resources" / "examples" / "2324.txt"
SNAPSHOT = CURR_DIR / "snapshot.json"


def test_parse_rfc():
    doc_text = DOC_TO_TEST.read_text()
    result = parse_rfc(doc_text)
    expected = ParsedDocument.model_validate_json(SNAPSHOT.read_text())
    assert expected == result
