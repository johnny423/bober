import datetime
from pathlib import Path

import pytest

from bober.src.rfc_ingest.load_from_file import load_single_file
from bober.src.search.rfc_content import (
    get_absolute_positions,
    load_rfc_content,
)

CURR_DIR = Path(__file__).parent
DOC_TO_TEST = CURR_DIR.parent / "resources" / "examples" / "2324.txt"


@pytest.fixture
def rfc_num():
    return 2324


@pytest.fixture
def load_rfc(db_session, rfc_num):
    load_single_file(
        db_session,
        DOC_TO_TEST,
        {
            "num": rfc_num,
            "title": "hellp",
            "publish_at": datetime.date.today(),
            "authors": ["Eli"],
        },
    )

def test_round_trip(db_session, rfc_num, load_rfc):
    """
    dump content into database and reload it should be the same
    """

    loaded = load_rfc_content(db_session, rfc_num)

    original = DOC_TO_TEST.read_text().rstrip()
    assert original == loaded


def test_abs_position(db_session, rfc_num, load_rfc):
    original = DOC_TO_TEST.read_text().rstrip().splitlines()
    positions = get_absolute_positions(db_session, rfc_num, "protocol")

    assert len(positions)

    for pos in positions:
        value = original[pos.line - 1][pos.slice()]
        assert value.lower() in ["protocol", "protocols"]
