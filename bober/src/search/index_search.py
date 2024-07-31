from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from bober.src.db_models import Rfc, RfcLine, RfcSection, Token, TokenPosition


@dataclass
class Index1Criteria:
    title: None | str = None
    page: None | int = None
    line_in_page: None | int = None
    position_in_line: None | int = None


@dataclass
class Index2Criteria:
    title: None | str = None
    section: None | int = None
    line_in_section: None | int = None
    position_in_line: None | int = None


@dataclass
class SearchResult:
    word: str
    context: str


# todo: add links to source? + inline with words index
def index_1_search(
        session: Session, criteria: Index1Criteria
) -> list[SearchResult]:
    query = (
        select(
            Token.token,
            TokenPosition,
            Rfc.title,
            RfcLine.line_number,
            RfcSection.row_start,
            RfcSection.page.label("page_number")
        )
        .join(Token.positions)
        .join(TokenPosition.line)
        .join(RfcLine.section)
        .join(RfcSection.rfc)
        .order_by(RfcSection.page, RfcLine.id, TokenPosition.start_position)
    )

    if criteria.title:
        query = query.where(Rfc.title.ilike(f"%{criteria.title}%"))
    if criteria.page is not None:
        query = query.where(RfcSection.page == criteria.page)
    if criteria.line_in_page is not None:
        query = query.where(
            (RfcLine.line_number + RfcSection.row_start) == criteria.line_in_page
        )
    if criteria.position_in_line is not None:
        query = query.where(TokenPosition.start_position == criteria.position_in_line)

    results = session.execute(query).all()
    return [
        SearchResult(
            word=result.token,
            context=f"Page {result.page_number}, Line {result.line_number + result.row_start}, Position {result.TokenPosition.start_position}",
        )
        for result in results
    ]


def index_2_search(
        session: Session, criteria: Index2Criteria
) -> list[SearchResult]:
    query = (
        select(
            Token.token,
            TokenPosition,
            Rfc.title,
            RfcLine.line_number,
            RfcSection.page
        )
        .join(Token.positions)
        .join(TokenPosition.line)
        .join(RfcLine.section)
        .join(RfcSection.rfc)
        .order_by(RfcSection.index, RfcLine.id, TokenPosition.start_position)
    )

    if criteria.title:
        query = query.where(Rfc.title.ilike(f"%{criteria.title}%"))
    if criteria.section is not None:
        query = query.where(RfcSection.index == criteria.section)
    if criteria.line_in_section is not None:
        query = query.where(RfcLine.line_number == criteria.line_in_section)
    if criteria.position_in_line is not None:
        query = query.where(TokenPosition.start_position == criteria.position_in_line)

    results = session.execute(query).all()
    return [
        SearchResult(
            word=result.token,
            context=f"Section {result.RfcSection.index}, Line {result.line_number}, Position {result.TokenPosition.start_position}",
        )
        for result in results
    ]
