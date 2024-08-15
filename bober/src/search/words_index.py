from dataclasses import dataclass, field
from enum import StrEnum
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bober.src.db_models import (
    Rfc,
    RfcLine,
    RfcSection,
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
    occurrences: List[TokenOccurrence] = field(default_factory=list)

    @property
    def count(self):
        return len(self.occurrences)


@dataclass
class WordIndex:
    token: str
    rfc_occurrences: Dict[int, RfcOccurrences] = field(default_factory=dict)

    @property
    def total_count(self):
        return sum(rfc.count for rfc in self.rfc_occurrences.values())


class SortBy(StrEnum):
    OCCURRENCES = "occurrences"
    ALPHABETICAL = "alphabetical"
    RFC_DATE = "rfc_date"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


def query_words_index(
    session: Session,
    token_groups: Optional[List[str]] = None,
    rfc_title: Optional[str] = None,
    partial_token: Optional[str] = None,
    sort_by: SortBy = SortBy.OCCURRENCES,
    sort_order: SortOrder = SortOrder.DESC,
) -> Dict[str, WordIndex]:
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
    )

    if token_groups is not None:
        query = query.join(Token.token_groups).join(TokenToGroup.group)
        query = query.filter(TokenGroup.group_name.in_(token_groups))

    if rfc_title is not None:
        query = query.filter(Rfc.title.ilike(f"%{rfc_title}%"))

    if partial_token is not None:
        query = query.filter(Token.token.ilike(f'%{partial_token}%'))

    order_by_clause = {
        SortBy.OCCURRENCES: func.count().over(partition_by=Token.token),
        SortBy.ALPHABETICAL: Token.token,
        SortBy.RFC_DATE: Rfc.published_at,
    }[sort_by]

    if sort_order == SortOrder.DESC:
        order_by_clause = order_by_clause.desc()

    query = query.order_by(
        order_by_clause,
        Rfc.num,
        RfcSection.index,
        RfcLine.id,
        TokenPosition.index,
    )

    result: Dict[str, WordIndex] = {}
    for res in session.execute(query):
        if res.token not in result:
            result[res.token] = WordIndex(token=res.token)

        if res.rfc_num not in result[res.token].rfc_occurrences:
            result[res.token].rfc_occurrences[res.rfc_num] = RfcOccurrences(
                title=res.rfc_title
            )

        occurrence = TokenOccurrence(
            abs_line=res.abs_line,
            section_index=res.section_index,
            page=res.page,  # We don't have page information in the new model
            row=res.row_start + res.line_in_section,
            context=res.context,  # todo: content should might include lines before and after
            start_position=res.start_position,
            end_position=res.end_position,
            index=res.index,
        )

        result[res.token].rfc_occurrences[res.rfc_num].occurrences.append(occurrence)

    return result
