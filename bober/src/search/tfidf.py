from sqlalchemy import Float, func
from sqlalchemy.orm import Query, Session

from bober.src.db_models import Rfc, RfcLine, RfcSection, Token, TokenPosition
from bober.src.parsing.parsed_types import STEMMER


def build_tfid_query(session: Session, tokens: list[str]) -> Query:
    stems = [STEMMER.stem(token.lower()) for token in tokens]

    term_frequency = (
        session.query(
            RfcLine.section_id,
            Token.stem,
            func.count(TokenPosition.id).label('tf'),
        )
        .join(TokenPosition.token)
        .join(TokenPosition.line)
        .filter(Token.stem.in_(stems))
        .group_by(RfcLine.section_id, Token.stem)
        .subquery()
    )

    document_frequency = (
        session.query(
            Token.stem,
            func.count(func.distinct(RfcSection.rfc_num)).label('df'),
        )
        .join(Token.positions)
        .join(TokenPosition.line)
        .join(RfcLine.section)
        .filter(Token.stem.in_(stems))
        .group_by(Token.stem)
        .subquery()
    )

    total_documents = session.query(func.count(Rfc.num)).scalar_subquery()

    tfidf = (
        session.query(
            RfcSection.rfc_num,
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
        .join(RfcSection, RfcSection.id == term_frequency.c.section_id)
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
