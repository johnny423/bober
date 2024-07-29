from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from bober.src.db_models import Rfc, RfcLine, RfcSection, Token, TokenPosition


@dataclass
class Index1Criteria:
    title: None | str = None
    page: None | int = None
    line: None | int = None
    position: None | int = None


@dataclass
class Index2Criteria:
    title: None | str = None
    section: None | int = None
    line: None | int = None
    position: None | int = None


@dataclass
class SearchResult:
    word: str
    context: str


def index_1_search(
        session: Session, criteria: Index1Criteria
) -> list[SearchResult]:
    query = (
        select(
            Token.token,
            TokenPosition,
            Rfc.title,
            RfcLine.id.label('line_number'),
            RfcSection.page.label("page_number")
        )
        .join(TokenPosition, Token.id == TokenPosition.token_id)
        .join(RfcLine, TokenPosition.line_id == RfcLine.id)
        .join(RfcSection, RfcLine.section_id == RfcSection.id)
        .join(Rfc, RfcSection.rfc_num == Rfc.num)
        .order_by(RfcSection.page, RfcLine.id, TokenPosition.start_position)
    )

    if criteria.title:
        query = query.where(Rfc.title.ilike(f"%{criteria.title}%"))
    if criteria.page is not None:
        query = query.where(RfcSection.page == criteria.page)
    if criteria.line is not None:
        query = query.where(RfcLine.id == criteria.line)
    if criteria.position is not None:
        query = query.where(TokenPosition.start_position == criteria.position)

    results = session.execute(query).all()
    return [
        SearchResult(
            word=result.token,
            context=f"Page {result.page_number}, Line {result.line_number}, Position {result.TokenPosition.start_position}",
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
            RfcSection,
            RfcLine.id.label('line_number'),
            Rfc.title,
        )
        .join(TokenPosition, Token.id == TokenPosition.token_id)
        .join(RfcLine, TokenPosition.line_id == RfcLine.id)
        .join(RfcSection, RfcLine.section_id == RfcSection.id)
        .join(Rfc, RfcSection.rfc_num == Rfc.num)
        .order_by(RfcSection.index, RfcLine.id, TokenPosition.start_position)
    )

    if criteria.title:
        query = query.where(Rfc.title.ilike(f"%{criteria.title}%"))
    if criteria.section is not None:
        query = query.where(RfcSection.index == criteria.section)
    if criteria.line is not None:
        query = query.where(RfcLine.id == criteria.line)
    if criteria.position is not None:
        query = query.where(TokenPosition.start_position == criteria.position)

    results = session.execute(query).all()
    return [
        SearchResult(
            word=result.token,
            context=f"Section {result.RfcSection.index}, Line {result.line_number}, Position {result.TokenPosition.start_position}",
        )
        for result in results
    ]
