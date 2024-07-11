from datetime import date

from sqlalchemy import func, distinct

from bober.src.db_models import Token, TokenPosition, Rfc, Author, TokenToGroup, TokenGroup, RfcSection


def search_words(
        session,
        rfc_title: None | str = None,
        author_name: None | str = None,
        date_from: None | date = None,
        date_to: None | date = None,
        word_groups: None | list[str] = None,
) -> list:
    query = session.query(
        Token.token,
        func.count(distinct(TokenPosition.rfc_num)).label('rfc_count'),
        func.count(TokenPosition.id).label('total_occurrences')
    ).join(TokenPosition).join(Rfc)

    # Apply filters
    if rfc_title:
        query = query.filter(Rfc.title.ilike(f"%{rfc_title}%"))
    if author_name:
        query = query.join(Author).filter(Author.author_name.ilike(f"%{author_name}%"))
    if date_from:
        query = query.filter(Rfc.published_at >= date_from)
    if date_to:
        query = query.filter(Rfc.published_at <= date_to)
    if word_groups:
        query = query.join(TokenToGroup).join(TokenGroup).filter(TokenGroup.group_name.in_(word_groups))

    # Group and order
    query = query.group_by(Token.token).order_by(Token.token)

    return query.all()


def get_token_positions(
        session,
        tokens: list[str],
        rfc_ids: list[int] | None = None
):
    query = session.query(
        Token.token,
        TokenPosition.rfc_num,
        TokenPosition.page,
        TokenPosition.row,
        RfcSection.id,
        RfcSection.index
    ).join(Token).join(RfcSection)

    query = query.filter(Token.token.in_(tokens))

    if rfc_ids:
        query = query.filter(TokenPosition.rfc_num.in_(rfc_ids))

    return query.all()
