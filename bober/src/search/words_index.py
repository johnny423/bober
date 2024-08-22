from dataclasses import dataclass, field
from enum import StrEnum

from sqlalchemy import desc, func, select
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


# todo: rename
@dataclass
class RfcOccurrences2:
    title: str
    num: int
    count: int


@dataclass
class RfcOccurrences:
    title: str
    occurrences: list[TokenOccurrence] = field(default_factory=list)

    @property
    def count(self):
        return len(self.occurrences)


@dataclass
class WordIndex:
    token: str
    rfc_occurrences: dict[int, RfcOccurrences] = field(default_factory=dict)

    @property
    def count_occurrences(self):
        return sum(rfc.count for rfc in self.rfc_occurrences.values())


class SortBy(StrEnum):
    ALPHABETICAL = "alphabetical"
    OCCURRENCES = "occurrences"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


def query_filtered_words(
    session: Session,
    token_groups: list[str] | None = None,
    rfc_title: str | None = None,
    partial_token: str | None = None,
    sort_by: SortBy = SortBy.ALPHABETICAL,
    sort_order: SortOrder = SortOrder.DESC,
    limit: int = 100,
) -> tuple[list[tuple[str, int]], int]:
    query = (
        select(
            Token.stem, func.sum(RfcTokenCount.total_positions).label('count')
        )
        .select_from(Token)
        .join(RfcTokenCount, Token.id == RfcTokenCount.token_id)
        .join(Rfc, RfcTokenCount.rfc_num == Rfc.num)
    )

    if token_groups is not None:
        query = query.filter(
            Token.id.in_(
                select(TokenToGroup.token_id)
                .join(TokenGroup)
                .filter(TokenGroup.group_name.in_(token_groups))
            )
        )

    if rfc_title is not None:
        query = query.filter(Rfc.title.ilike(f"%{rfc_title}%"))

    if partial_token is not None:
        query = query.filter(Token.token.ilike(f'%{partial_token}%'))

    # Add GROUP BY to the base query
    query = query.group_by(Token.stem)

    # Calculate total count
    total_count_query = select(func.count()).select_from(query.subquery())
    total_count = session.execute(total_count_query).scalar_one()

    # Apply ordering to the main query
    order_by_clause = 'count' if sort_by == SortBy.OCCURRENCES else Token.stem

    if sort_order == SortOrder.DESC:
        order_by_clause = desc(order_by_clause)

    query = query.order_by(order_by_clause).limit(limit)
    results = session.execute(query).fetchall()

    limited_words = [(line[0], line[1]) for line in results]
    return limited_words, total_count


def fetch_rfc_occurrences(
    session: Session, stem: str, rfc_title: None | str = None
) -> list[RfcOccurrences2]:
    query = (
        select(RfcTokenCount.total_positions, Rfc.num, Rfc.title)
        .select_from(RfcTokenCount)
        .join(Token, Token.id == RfcTokenCount.token_id)
        .join(Rfc, RfcTokenCount.rfc_num == Rfc.num)
        .filter(Token.stem == stem)
    )

    if rfc_title:
        query = query.filter(Rfc.title.ilike(f"%{rfc_title}%"))

    results = []
    for res in session.execute(query):
        results.append(
            RfcOccurrences2(
                title=res.title, num=res.num, count=res.total_positions
            )
        )

    return results


def fetch_occurrences(
    session: Session, stem: str, rfc_num: int
) -> list[TokenOccurrence]:
    query = (
        select(
            Token.stem.label("token"),
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
        .filter(Token.stem == stem)
        .filter(Rfc.num == rfc_num)
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
