from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from bober.src.db_models import Rfc, RfcLine, RfcSection, Token, TokenPosition


@dataclass
class AbsPositionQuery:
    title: None | str = None
    abs_line: None | int = None
    column: None | int = None


@dataclass
class RelativePositionQuery:
    title: None | str = None
    section: None | int = None
    line_in_section: None | int = None
    word_in_line: None | int = None


@dataclass
class SearchResult:
    rfc: int
    stem: str
    word: str
    context: str
    abs_line: int


def abs_position_search(
    session: Session, criteria: AbsPositionQuery
) -> list[SearchResult]:
    query = (
        select(
            Rfc.num,
            RfcLine.abs_line_number.label("abs_line"),
            Token.token,
            Token.stem,
            TokenPosition.start_position,
            RfcLine.indentation,
        )
        .join(Token.positions)
        .join(TokenPosition.line)
        .join(RfcLine.section)
        .join(RfcSection.rfc)
        .order_by(RfcLine.abs_line_number, TokenPosition.start_position)
    )

    if criteria.title:
        query = query.where(Rfc.title.ilike(f"%{criteria.title}%"))

    if criteria.abs_line is not None:
        query = query.where(RfcLine.abs_line_number == credits.abs_line)

    if criteria.column is not None:
        query = query.where(
            (
                (RfcLine.indentation + TokenPosition.start_position)
                <= criteria.column
            )
            & (
                (RfcLine.indentation + TokenPosition.end_position)
                >= criteria.column
            )
        )

    results = session.execute(query).all()
    return [
        SearchResult(
            rfc=result.num,
            abs_line=result.abs_line,
            stem=result.stem,
            word=result.token,
            context=f"Line {result.abs_line}, Start Column {result.indentation + result.start_position}",
        )
        for result in results
    ]


def relative_position_search(
    session: Session, criteria: RelativePositionQuery
) -> list[SearchResult]:
    query = (
        select(
            Rfc.num,
            RfcLine.abs_line_number.label("abs_line"),
            Token.token,
            Token.stem,
            RfcLine.line_number,
            TokenPosition.index.label("word_index"),
            RfcSection.index.label("section_index"),
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
    if criteria.word_in_line is not None:
        query = query.where(TokenPosition.index == criteria.word_in_line)

    results = session.execute(query).all()
    return [
        SearchResult(
            rfc=result.num,
            abs_line=result.abs_line,
            stem=result.stem,
            word=result.token,
            context=f"Section {result.section_index}, Line {result.line_number}, Word {result.word_index}",
        )
        for result in results
    ]
