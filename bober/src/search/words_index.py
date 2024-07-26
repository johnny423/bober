from dataclasses import dataclass, field
from enum import StrEnum

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bober.src.db_models import Token, Rfc, RfcSection, TokenPosition, TokenGroup, TokenToGroup


@dataclass
class WordOccurrence:
    section_index: int
    page: int
    row: int
    position: int
    index: int
    context: str


@dataclass
class RfcOccurrences:
    title: str
    occurrences: list[WordOccurrence] = field(default_factory=list)

    @property
    def count(self):
        return len(self.occurrences)


@dataclass
class WordIndex:
    token: str
    rfc_occurrences: dict[int, RfcOccurrences] = field(default_factory=dict)

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
        token_groups: None | list[str] = None,
        rfc_title: None | str = None,
        partial_token: None | str = None,
        sort_by: SortBy = SortBy.OCCURRENCES,
        sort_order: SortOrder = SortOrder.DESC
) -> dict[str, WordIndex]:
    query = (
        select(
            Token.stem,
            Rfc.num,
            Rfc.title,
            Rfc.published_at,
            RfcSection.index.label('section_index'),
            TokenPosition.page,
            TokenPosition.row,
            TokenPosition.position,
            TokenPosition.index,
            RfcSection.content,
            func.count().over(partition_by=Token.token).label('token_count')
        )
        .join(Token.token_positions)
        .join(TokenPosition.rfc)
        .join(TokenPosition.section)
    )

    if token_groups is not None:
        query = query.join(Token.token_groups).join(TokenToGroup.group)
        query = query.filter(TokenGroup.group_name.in_(token_groups))

    if rfc_title is not None:
        query = query.filter(Rfc.title.ilike(f"'%{rfc_title}%'"))

    if partial_token is not None:
        query = query.filter(Token.token.ilike(f'%{partial_token}%'))

    order_by_clause = {
        SortBy.OCCURRENCES: func.count().over(partition_by=Token.token),
        SortBy.ALPHABETICAL: Token.token,
        SortBy.RFC_DATE: Rfc.published_at
    }[sort_by]

    if sort_order == SortOrder.DESC:
        order_by_clause = order_by_clause.desc()

    query = query.order_by(order_by_clause, Rfc.num, RfcSection.index, TokenPosition.page, TokenPosition.row)

    result: dict[str, WordIndex] = {}
    for (token, rfc_num, rfc_title, published_at, section_index,
         page, row, position, index, section_content, token_count) in session.execute(query):

        if token not in result:
            result[token] = WordIndex(token=token)

        if rfc_num not in result[token].rfc_occurrences:
            result[token].rfc_occurrences[rfc_num] = RfcOccurrences(title=rfc_title)

        occurrence = WordOccurrence(
            section_index=section_index,
            page=page,
            row=row,
            context=section_content,
            position=position,
            index=index
        )

        result[token].rfc_occurrences[rfc_num].occurrences.append(occurrence)

    return result
