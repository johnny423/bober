from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bober.src.db import commit
from bober.src.db_models import (
    Phrase,
    PhraseToken,
    Rfc,
    RfcLine,
    RfcSection,
    Token,
    TokenPosition,
)


@commit
def save_new_phrase(session: Session, phrase_name: str, phrase: str):
    words = phrase.split()

    existing_tokens = {
        token.token: token.id
        for token in session.query(Token)
        .filter(Token.token.in_(set(words)))
        .all()
    }

    phrase_tokens = []
    for index, token in enumerate(words):
        token_id = existing_tokens.get(token, None)
        if token_id is None:
            raise ValueError(
                f"The word {token} does not exist in the database."
            )

        phrase_token = PhraseToken(token_id=token_id, index=index)
        phrase_tokens.append(phrase_token)

    new_phrase = Phrase(
        phrase_name=phrase_name, content=phrase, tokens=phrase_tokens
    )
    session.add(new_phrase)


def find_phrase_occurrences(session: Session, phrase_name: str):
    phrase = (
        session.query(Phrase)
        .filter(Phrase.phrase_name == phrase_name)
        .one_or_none()
    )
    if not phrase:
        raise ValueError(f"Phrase with name {phrase_name} does not exist.")

    return search_phrase(session, phrase.content)


def search_phrase(session: Session, phrase: str):
    tokens = phrase.lower().split()
    token_count = len(tokens)

    def aggregate(field):
        return func.array_agg(field).over(
            partition_by=[
                RfcSection.rfc_num,
                RfcSection.index,
            ],
            order_by=[TokenPosition.abs_index],
            rows=(0, token_count - 1),
        )

    token_windows_query = (
        select(
            Token.token,
            Rfc.num.label('rfc_num'),
            Rfc.title.label('rfc_title'),
            RfcSection.index.label('section_index'),
            RfcLine.abs_line_number,
            RfcLine.indentation,
            func.array_to_string(aggregate(Token.token), ' ').label('phrase'),
            aggregate(TokenPosition.abs_index).label('indexes'),
            aggregate(TokenPosition.start_position).label('start_pos'),
            aggregate(TokenPosition.end_position).label('end_pos'),
        )
        .filter(Token.token.in_(tokens))
        .join(TokenPosition, Token.id == TokenPosition.token_id)
        .join(RfcLine, TokenPosition.line_id == RfcLine.id)
        .join(RfcSection, RfcLine.section_id == RfcSection.id)
        .join(Rfc, RfcSection.rfc_num == Rfc.num)
        .subquery()
    )

    search_query = (
        select(
            token_windows_query.c.rfc_num,
            token_windows_query.c.rfc_title,
            token_windows_query.c.section_index,
            token_windows_query.c.phrase,
            token_windows_query.c.abs_line_number,
            token_windows_query.c.indentation,
            token_windows_query.c.start_pos[1].label("start_pos"),
            token_windows_query.c.end_pos[token_count].label("end_pos"),
        )
        .select_from(token_windows_query)
        .where(
            (func.lower(token_windows_query.c.phrase) == phrase.lower())
            & (
                func.array_length(token_windows_query.c.indexes, 1)
                == (
                    token_windows_query.c.indexes[token_count]
                    - token_windows_query.c.indexes[1]
                    + 1
                )
            )
        )
    )

    return session.execute(search_query).all()
