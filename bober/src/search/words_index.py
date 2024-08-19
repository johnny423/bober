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


@dataclass
class TokenOccurrence:
    abs_line: int
    section_index: int
    page: int
    row: int
    start_position: int
    end_position: int
    index: int
    context: str


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
) -> list[tuple[str, int]]:
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

    query = query.group_by(Token.stem)

    order_by_clause = (
        func.sum(RfcTokenCount.total_positions)
        if sort_by == SortBy.OCCURRENCES
        else Token.stem
    )

    if sort_order == SortOrder.DESC:
        order_by_clause = desc(order_by_clause)

    query = query.order_by(order_by_clause).limit(limit)
    results = session.execute(query).fetchall()

    limited_words = [(row[0], row[1]) for row in results]
    return limited_words


def fetch_occurrences(
    session: Session, stem: str, rfc_title: None | str = None
) -> dict[int, RfcOccurrences]:
    query = (
        select(
            Token.stem.label("token"),
            RfcLine.abs_line_number.label("abs_line"),
            Rfc.num.label("rfc_num"),
            Rfc.title.label("rfc_title"),
            RfcSection.index.label('section_index'),
            RfcSection.page,
            RfcSection.row_start,
            RfcLine.line_number.label('line_in_section'),
            TokenPosition.start_position,
            TokenPosition.end_position,
            TokenPosition.index,
            RfcLine.line.label('context'),
        )
        .join(Token.positions)
        .join(TokenPosition.line)
        .join(RfcLine.section)
        .join(RfcSection.rfc)
        .filter(Token.stem == stem)
    )

    if rfc_title:
        query = query.filter(Rfc.title.ilike(f"%{rfc_title}%"))

    rfc_occurrences = {}
    for res in session.execute(query):
        if res.rfc_num not in rfc_occurrences:
            rfc_occurrences[res.rfc_num] = RfcOccurrences(title=res.rfc_title)

        occurrence = TokenOccurrence(
            abs_line=res.abs_line,
            section_index=res.section_index,
            page=res.page,
            row=res.row_start + res.line_in_section,
            context=res.context,
            start_position=res.start_position,
            end_position=res.end_position,
            index=res.index,
        )

        rfc_occurrences[res.rfc_num].occurrences.append(occurrence)

    return rfc_occurrences
