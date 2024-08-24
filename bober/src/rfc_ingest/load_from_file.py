import datetime
from pathlib import Path
from typing import TypedDict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bober.src.db import commit
from bober.src.db_models import (
    OrderedToken,
    Rfc,
    RfcLine,
    RfcSection,
    Token,
    TokenPosition,
)
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

    rfc_num = rfc_metadata["num"]
    ingest_rfc(
        session,
        rfc_num=rfc_num,
        rfc_title=rfc_metadata["title"],
        rfc_published_at=rfc_metadata["publish_at"],
        rfc_authors=rfc_metadata["authors"],
        parsed_doc=parsed_doc,
    )

    populate_ordered_tokens(session, rfc_num)


@commit
def populate_ordered_tokens(session, rfc_num):
    ordered_tokens_query = (
        select(
            Token.token,
            Rfc.num.label('rfc_num'),
            Rfc.title.label('rfc_title'),
            RfcSection.index.label('section_index'),
            RfcLine.abs_line_number,
            func.row_number()
            .over(
                order_by=[
                    Rfc.num,
                    RfcSection.page,
                    RfcSection.index,
                    RfcLine.line_number,
                    TokenPosition.index,
                ]
            )
            .label('row_num'),
        )
        .join(TokenPosition, Token.id == TokenPosition.token_id)
        .join(RfcLine, TokenPosition.line_id == RfcLine.id)
        .join(RfcSection, RfcLine.section_id == RfcSection.id)
        .join(Rfc, RfcSection.rfc_num == Rfc.num)
        .filter(Rfc.num == rfc_num)
    )

    for result in session.execute(ordered_tokens_query).fetchall():
        ordered_token = OrderedToken(
            token=result.token,
            rfc_num=result.rfc_num,
            rfc_title=result.rfc_title,
            section_index=result.section_index,
            abs_line_number=result.abs_line_number,
            row_num=result.row_num,
        )
        session.add(ordered_token)
