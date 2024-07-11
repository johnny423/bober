from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session

from bober.src.db_models import Rfc, Author
from bober.src.search.tfidf import build_tfid_query


class RFCMeta(BaseModel):
    num: int
    title: str
    published_at: datetime
    authors: list[str]


class SearchRFCQuery(BaseModel):
    authors: list[str] | None = None
    date_range: tuple[datetime, datetime] | None = None
    title: str | None = None
    tokens: list[str] | None = None


def search_rfcs(
    session: Session, search_query: SearchRFCQuery
) -> list[RFCMeta]:
    query = session.query(
        Rfc.num, Rfc.title, Rfc.published_at
    )  # .options(joinedload(Rfc.authors))

    # Apply filters based on provided parameters
    if search_query.authors:
        author_filters = [
            Author.author_name.ilike(f"%{author}%")
            for author in search_query.authors
        ]
        query = query.join(Author).filter(and_(*author_filters))

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
    else:
        query = query.order_by(desc(Rfc.published_at))

    output = []
    for result in query.all():
        rfc_dict = RFCMeta(
            num=result.num,
            title=result.title,
            published_at=result.published_at.isoformat(),
            authors=[],  # [author.author_name for author in result.authors],
        )

        output.append(rfc_dict)

    return output
