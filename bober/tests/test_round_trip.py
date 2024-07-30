import datetime
from pathlib import Path

from bober.src.rfc_ingest.load_from_file import load_single_file
from bober.src.search.rfc_content import load_rfc_content

CURR_DIR = Path(__file__).parent
DOC_TO_TEST = CURR_DIR.parent / "resources" / "examples" / "2324.txt"


def test_round_trip(db_session):
    """
    dump content into database and reload it should be the same
    """
    RFC_NUM = 2324

    load_single_file(
        db_session,
        DOC_TO_TEST,
        {
            "num": RFC_NUM,
            "title": "hellp",
            "publish_at": datetime.date.today(),
        }
    )

    loaded = load_rfc_content(db_session, RFC_NUM)

    original = DOC_TO_TEST.read_text().rstrip()
    assert original == loaded
