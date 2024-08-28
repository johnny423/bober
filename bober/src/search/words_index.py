from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy import desc, func, select, or_
from sqlalchemy.orm import Session

from bober.src.db_models import (
    Rfc,
    RfcLine,
    RfcSection,
    RfcTokenCount,
    Token,
    TokenGroup,
    TokenPosition,
    TokenToGroup,
)
from bober.src.fe.utils import ellipsis_around
from bober.src.search.positions import AbsPosition, RelativePosition


@dataclass
class TokenContext:
    content: str
    start_pos: int
    end_pos: int

    def shorten(self, max_length) -> str:
        return ellipsis_around(
            self.content,
            self.start_pos,
            self.end_pos,
            max_length,
        )


@dataclass
class TokenOccurrence:
    page: int
    abs_pos: AbsPosition
    rel_pos: RelativePosition
    context: TokenContext


@dataclass
class RfcOccurrences:
    title: str
    num: int
    count: int


class SortBy(StrEnum):
    ALPHABETICAL = "alphabetical"
    OCCURRENCES = "occurrences"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass
class QueryFilteredWordsParams:
    token_groups: list[str] | None = None
    rfc_title: str | None = None
    partial_token: str | None = None
    sort_by: SortBy = SortBy.ALPHABETICAL
    sort_order: SortOrder = SortOrder.DESC
    page: int = 1
    page_size: int = 100


@dataclass
class QueryFilteredWordsResult:
    words: list[tuple[str, str, int]]
    total_count: int


def query_filtered_words(
    session: Session, params: QueryFilteredWordsParams
) -> QueryFilteredWordsResult:
    query = (
        select(
            Token.token, Token.stem, func.sum(RfcTokenCount.total_positions).label('count')
        )
        .select_from(Token)
        .join(RfcTokenCount, Token.id == RfcTokenCount.token_id)
        .join(Rfc, RfcTokenCount.rfc_num == Rfc.num)
    )

    if params.token_groups is not None:
        query = query.filter(
            Token.id.in_(
                select(TokenToGroup.token_id)
                .join(TokenGroup)
                .filter(TokenGroup.group_name.in_(params.token_groups))
            )
        )

    if params.rfc_title is not None:
        query = query.filter(Rfc.title.ilike(f"%{params.rfc_title}%"))

    if params.partial_token is not None:
        # todo maybe get the stems of all tokens that have this substring and filter by these stems
        # todo (in addition to stem containing the substring)
        query = query.filter(
            or_(
                Token.token.ilike(f'%{params.partial_token}%'),
                Token.stem.ilike(f'%{params.partial_token}%'),
            )
        )

    # Add GROUP BY to the base query
    query = query.group_by(Token.token, Token.stem)

    # Calculate total count
    total_count_query = select(func.count()).select_from(query.subquery())
    total_count = session.execute(total_count_query).scalar_one()

    # Apply ordering to the main query
    order_by_clause = (
        'count' if params.sort_by == SortBy.OCCURRENCES else Token.token
    )

    if params.sort_order == SortOrder.DESC:
        order_by_clause = desc(order_by_clause)

    # Calculate offset from page number and page size
    offset = (params.page - 1) * params.page_size

    query = (
        query.order_by(order_by_clause).offset(offset).limit(params.page_size)
    )
    results = session.execute(query).fetchall()

    words = [(line[0], line[1], line[2]) for line in results]
    return QueryFilteredWordsResult(
        words=words,
        total_count=total_count,
    )


def fetch_rfc_occurrences(
    session: Session, token: str, rfc_title: None | str = None
) -> list[RfcOccurrences]:
    query = (
        select(
            Rfc.num,
            Rfc.title,
            func.sum(RfcTokenCount.total_positions).label("count"),
        )
        .select_from(RfcTokenCount)
        .join(Token, Token.id == RfcTokenCount.token_id)
        .join(Rfc, RfcTokenCount.rfc_num == Rfc.num)
        .filter(Token.token == token)
        .group_by(Rfc.num, Rfc.title)
    )

    if rfc_title:
        query = query.filter(Rfc.title.ilike(f"%{rfc_title}%"))

    results = []
    for res in session.execute(query):
        results.append(
            RfcOccurrences(title=res.title, num=res.num, count=res.count)
        )

    return results


def fetch_occurrences(
    session: Session, token: str, rfc_num: int
) -> list[TokenOccurrence]:
    query = (
        select(
            Token.token.label("token"),
            RfcLine.abs_line_number.label("abs_line"),
            Rfc.num.label("rfc_num"),
            Rfc.title.label("rfc_title"),
            RfcLine.indentation,
            RfcSection.index.label('section_index'),
            RfcSection.page,
            RfcSection.row_start,
            RfcLine.line_number.label('line_in_section'),
            TokenPosition.start_position,
            TokenPosition.end_position,
            TokenPosition.index.label("word_index"),
            RfcLine.line.label('content'),
        )
        .join(Token.positions)
        .join(TokenPosition.line)
        .join(RfcLine.section)
        .join(RfcSection.rfc)
        .filter(Token.token == token)
        .filter(Rfc.num == rfc_num)
        .order_by(TokenPosition.abs_index.asc())
    )

    results = []
    for res in session.execute(query):
        occurrence = TokenOccurrence(
            page=res.page,
            abs_pos=AbsPosition(
                line=res.abs_line,
                column=res.indentation + res.start_position,
                length=res.end_position - res.start_position,
            ),
            rel_pos=RelativePosition(
                section=res.section_index,
                line=res.row_start + res.line_in_section,
                word=res.word_index,
            ),
            context=TokenContext(
                content=res.content,
                start_pos=res.start_position,
                end_pos=res.end_position,
            ),
        )

        results.append(occurrence)

    return results
