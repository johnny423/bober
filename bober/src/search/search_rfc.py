from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Integer, or_, desc, func, and_, distinct, select, case
from sqlalchemy.orm import Session, selectinload

from bober.src.db_models import Author, Rfc
from bober.src.search.tfidf import build_tfid_query


class RFCMeta(BaseModel):
    num: int
    title: str
    published_at: datetime
    authors: list[str]
    rank: float | None


class SearchRFCQuery(BaseModel):
    num: int | None = None
    authors: list[str] | None = None
    date_range: tuple[datetime, datetime] | None = None
    title: str | None = None
    tokens: list[str] | None = None


def search_rfcs(
    session: Session, search_query: SearchRFCQuery
) -> list[RFCMeta]:
    query = session.query(Rfc).options(selectinload(Rfc.authors))

    if search_query.num:
        query = query.filter(Rfc.num == search_query.num)

    if search_query.authors:
        author_subquery = (
            select(Author.rfc_num)
            .where(
                or_(
                    *[Author.author_name.ilike(f"%{author}%")
                      for author in search_query.authors]
                )
            )
            .group_by(Author.rfc_num)
            .having(
                and_(
                    *[
                        func.count(
                            distinct(
                                case(
                                    (Author.author_name.ilike(f"%{author}%"), 1),
                                    else_=None
                                )
                            )
                        ) > 0
                        for author in search_query.authors
                    ]
                )
            )
        )

        query = query.filter(Rfc.num.in_(author_subquery))

    if search_query.date_range:
        start_date, end_date = search_query.date_range
        query = query.filter(Rfc.published_at.between(start_date, end_date))

    if search_query.title:
        query = query.filter(Rfc.title.ilike(f"%{search_query.title.lower()}%"))

    # If tokens are provided, calculate TF-IDF and rank results
    if search_query.tokens:
        tfidf_summary = build_tfid_query(
            session, search_query.tokens
        ).subquery()
        query = query.join(
            tfidf_summary, Rfc.num == tfidf_summary.c.rfc_num
        ).order_by(desc(tfidf_summary.c.total_tfidf_score))
        query = query.add_columns(
            tfidf_summary.c.total_tfidf_score.label("rank")
        )
    else:
        query = query.add_columns(func.cast(None, type_=Integer).label('rank'))
        query = query.order_by(desc(Rfc.published_at))

    output = []
    for rfc, rank in query.all():
        rfc_meta = RFCMeta(
            num=rfc.num,
            title=rfc.title,
            published_at=rfc.published_at,
            authors=[author.author_name for author in rfc.authors],
            rank=rank,
        )

        output.append(rfc_meta)

    return output
