from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bober.src.db import commit
from bober.src.db_models import (
    OrderedToken,
    Phrase,
    PhraseToken,
    Token,
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

    token_windows_query = (
        select(
            OrderedToken.rfc_num,
            OrderedToken.rfc_title,
            OrderedToken.section_index,
            OrderedToken.abs_line_number,
            func.array_to_string(
                func.array_agg(OrderedToken.token).over(
                    partition_by=[
                        OrderedToken.rfc_num,
                        OrderedToken.section_index,
                    ],
                    order_by=[OrderedToken.row_num],
                    rows=(0, token_count - 1),
                ),
                ' ',
            ).label('phrase'),
        ).filter(func.lower(OrderedToken.token).in_(tokens))
    ).subquery()

    search_query = (
        select(
            token_windows_query.c.rfc_num,
            token_windows_query.c.rfc_title,
            token_windows_query.c.section_index,
            token_windows_query.c.phrase,
            token_windows_query.c.abs_line_number,
        )
        .select_from(token_windows_query)
        .where(func.lower(token_windows_query.c.phrase) == phrase.lower())
    )

    return session.execute(search_query).all()
