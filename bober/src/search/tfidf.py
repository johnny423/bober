from sqlalchemy import Float, func
from sqlalchemy.orm import Query, Session

from bober.src.db_models import (
    Rfc,
    RfcTokenCount,
    Token,
)
from bober.src.parsing.parsed_types import STEMMER


def build_tfid_query(session: Session, tokens: list[str]) -> Query:
    stems = [STEMMER.stem(token.lower()) for token in tokens]

    term_frequency = (
        session.query(
            Token.stem,
            RfcTokenCount.rfc_num,
            RfcTokenCount.total_positions.label('tf'),
        )
        .join(Token.rfc_counts)
        .filter(Token.stem.in_(stems))
        .subquery()
    )

    document_frequency = (
        session.query(
            Token.stem,
            func.count(func.distinct(RfcTokenCount.rfc_num)).label('df'),
        )
        .join(Token.rfc_counts)
        .filter(Token.stem.in_(stems))
        .group_by(Token.stem)
        .subquery()
    )

    total_documents = session.query(func.count(Rfc.num)).scalar_subquery()

    tfidf = (
        session.query(
            Rfc.num.label("rfc_num"),
            term_frequency.c.stem,
            term_frequency.c.tf,
            document_frequency.c.df,
            total_documents.label('total_docs'),
            (
                term_frequency.c.tf
                * func.log(
                    total_documents.cast(Float)
                    / document_frequency.c.df.cast(Float)
                )
            ).label('tfidf_score'),
        )
        .join(Rfc, Rfc.num == term_frequency.c.rfc_num)
        .join(
            document_frequency,
            term_frequency.c.stem == document_frequency.c.stem,
        )
        .subquery()
    )

    tfidf_summary = session.query(
        tfidf.c.rfc_num,
        func.sum(tfidf.c.tfidf_score).label('total_tfidf_score'),
    ).group_by(tfidf.c.rfc_num)

    return tfidf_summary
