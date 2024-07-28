import datetime
from pathlib import Path
from typing import TypedDict

from sqlalchemy.orm import Session

from bober.src.db import commit
from bober.src.parsing.parse_rfc import parse_rfc
from bober.src.rfc_ingest.ingest_rfc import ingest_rfc


class RFCMetadata(TypedDict):
    num: int
    title: str
    publish_at: datetime.date
    authors: list[str]


@commit
def load_single_file(
    session: Session, file_path: str, rfc_metadata: RFCMetadata
):
    content = Path(file_path).read_text()
    parsed_doc = parse_rfc(content)

    ingest_rfc(
        session,
        rfc_num=rfc_metadata["num"],
        rfc_title=rfc_metadata["title"],
        rfc_published_at=rfc_metadata["publish_at"],
        parsed_doc=parsed_doc,
    )
