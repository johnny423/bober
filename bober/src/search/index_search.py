from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import select

from bober.src.db_models import Token, TokenPosition, Rfc, RfcSection


@dataclass
class SearchCriteria:
    title: None | str = None
    index_1_page: None | int = None
    index_1_row: None | int = None
    index_2_section: None | int = None
    index_2_word: None | str = None


@dataclass
class SearchResult:
    word: str
    context: str


def index_1_search(session, criteria: SearchCriteria) -> list[SearchResult]:
    query = (
        select(Token.token, TokenPosition, Rfc.title)
        .join(TokenPosition, Token.id == TokenPosition.token_id)
        .join(Rfc, TokenPosition.rfc_num == Rfc.num)
        .order_by(TokenPosition.row, TokenPosition.index)
    )

    if criteria.title:
        query = query.where(Rfc.title.ilike(f"%{criteria.title}%"))
    if criteria.index_1_page:
        query = query.where(TokenPosition.page == criteria.index_1_page)
    if criteria.index_1_row:
        query = query.where(TokenPosition.row == criteria.index_1_row)

    results = session.execute(query).all()
    return [
        SearchResult(
            word=result.token,
            context=f"Page {result.TokenPosition.page}, Row {result.TokenPosition.row}",
        )
        for result in results
    ]


def index_2_search(session, criteria: SearchCriteria) -> list[SearchResult]:
    query = (
        select(Token.token, RfcSection, Rfc.title)
        .join(TokenPosition, Token.id == TokenPosition.token_id)
        .join(RfcSection, TokenPosition.section_id == RfcSection.id)
        .join(Rfc, RfcSection.rfc_num == Rfc.num)
        .order_by(TokenPosition.row, TokenPosition.index)
    )
    if criteria.title:
        query = query.where(Rfc.title.ilike(f"%{criteria.title}%"))
    if criteria.index_2_section:
        query = query.where(RfcSection.index == criteria.index_2_section)
    if criteria.index_2_word:  # todo: whats the second index
        query = query.where(Token.token.ilike(f"%{criteria.index_2_word}%"))

    results = session.execute(query).all()
    return [
        SearchResult(
            word=result.token,
            context=f"Section {result.RfcSection.index}",
        )
        for result in results
    ]
