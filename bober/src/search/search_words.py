from datetime import date
from typing import List, Optional

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from bober.src.db_models import (
    Author,
    Rfc,
    RfcLine,
    RfcSection,
    Token,
    TokenGroup,
    TokenPosition,
    TokenToGroup,
)


def search_words(
    session: Session,
    rfc_title: Optional[str] = None,
    author_name: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    word_groups: Optional[List[str]] = None,
) -> List:
    query = (
        session.query(
            Token.token,
            func.count(distinct(Rfc.num)).label('rfc_count'),
            func.count(TokenPosition.id).label('total_occurrences'),
        )
        .join(Token.positions)
        .join(TokenPosition.line)
        .join(RfcLine.section)
        .join(RfcSection.rfc)
    )

    # Apply filters
    if rfc_title:
        query = query.filter(Rfc.title.ilike(f"%{rfc_title}%"))
    if author_name:
        query = query.join(Rfc.authors).filter(
            Author.author_name.ilike(f"%{author_name}%")
        )
    if date_from:
        query = query.filter(Rfc.published_at >= date_from)
    if date_to:
        query = query.filter(Rfc.published_at <= date_to)
    if word_groups:
        query = (
            query.join(Token.token_groups)
            .join(TokenToGroup.group)
            .filter(TokenGroup.group_name.in_(word_groups))
        )

    # Group and order
    query = query.group_by(Token.token).order_by(Token.token)

    return query.all()


def get_token_positions(
    session: Session, tokens: List[str], rfc_ids: Optional[List[int]] = None
):
    query = (
        session.query(
            Token.token,
            Rfc.num.label('rfc_num'),
            RfcLine.id.label('line_id'),
            RfcSection.id.label('section_id'),
            RfcSection.index.label('section_index'),
            TokenPosition.start_position,
            TokenPosition.end_position,
        )
        .join(Token.positions)
        .join(TokenPosition.line)
        .join(RfcLine.section)
        .join(RfcSection.rfc)
    )

    query = query.filter(Token.token.in_(tokens))

    if rfc_ids:
        query = query.filter(Rfc.num.in_(rfc_ids))

    return query.all()
