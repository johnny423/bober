from sqlalchemy import func, Float
from sqlalchemy.orm import Session, Query

from bober.src.db_models import TokenPosition, Token, Rfc
from bober.src.rfc_ingest.parsing import STEMMER


def build_tfid_query(session: Session, tokens: list[str]) -> Query:
    stems = [STEMMER.stem(token.lower()) for token in tokens]
    term_frequency = (
        session.query(
            TokenPosition.rfc_num,
            Token.stem,
            func.count(TokenPosition.id).label('tf'),
        )
        .join(Token)
        .filter(Token.stem.in_(stems))
        .group_by(TokenPosition.rfc_num, Token.stem)
        .subquery()
    )
    document_frequency = (
        session.query(
            Token.stem,
            func.count(func.distinct(TokenPosition.rfc_num)).label('df'),
        )
        .join(TokenPosition)
        .filter(Token.stem.in_(stems))
        .group_by(Token.stem)
        .subquery()
    )
    total_documents = session.query(func.count(Rfc.num)).scalar_subquery()
    tfidf = (
        session.query(
            term_frequency.c.rfc_num,
            term_frequency.c.stem,
            term_frequency.c.tf,
            document_frequency.c.df,
            total_documents.label('total_docs'),
            (
                    term_frequency.c.tf
                    * func.log(
                total_documents.cast(Float) / document_frequency.c.df
            )
            ).label('tfidf_score'),
        )
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
