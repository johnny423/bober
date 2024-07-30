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
            Token.stem,
            Rfc.num,
            Rfc.title,
            RfcSection.index.label('section_index'),
            RfcSection.page,
            RfcSection.row_start,
            RfcLine.line_number.label('line_in_page'),
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
    for (
            token,
            rfc_num,
            rfc_title,
            section_index,
            page,
            row_start,
            line_in_page,
            start_position,
            end_position,
            index,
            context,
    ) in session.execute(query):

        if token not in result:
            result[token] = WordIndex(token=token)

        if rfc_num not in result[token].rfc_occurrences:
            result[token].rfc_occurrences[rfc_num] = RfcOccurrences(
                title=rfc_title
            )

        occurrence = TokenOccurrence(
            section_index=section_index,
            page=page,  # We don't have page information in the new model
            row=row_start + line_in_page,
            context=context,  # todo: content should might include lines before and after
            start_position=start_position,
            end_position=end_position,
            index=index,
        )

        result[token].rfc_occurrences[rfc_num].occurrences.append(occurrence)

    return result
