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

    ordered_tokens = ordered_tokens_query().subquery()

    # Define the query to create token windows and search for the phrase
    token_windows_query = (
        select(
            ordered_tokens.c.rfc_num,
            ordered_tokens.c.rfc_title,
            ordered_tokens.c.section_index,
            ordered_tokens.c.page,
            ordered_tokens.c.abs_line_number,
            func.array_to_string(
                func.array_agg(ordered_tokens.c.token).over(
                    partition_by=[
                        ordered_tokens.c.rfc_num,
                        ordered_tokens.c.section_index,
                    ],
                    order_by=[ordered_tokens.c.row_num],
                    rows=(0, token_count - 1),
                ),
                ' ',
            ).label('phrase'),
        ).select_from(ordered_tokens)
    ).subquery()

    # Define the query to filter the windows by the input phrase
    search_query = (
        select(
            token_windows_query.c.rfc_num,
            token_windows_query.c.rfc_title,
            token_windows_query.c.section_index,
            token_windows_query.c.page,
            token_windows_query.c.phrase,
            token_windows_query.c.abs_line_number,
        )
        .select_from(token_windows_query)
        .where(func.lower(token_windows_query.c.phrase) == phrase.lower())
    )
    return session.execute(search_query).all()


def ordered_tokens_query():
    # Define the query to get ordered tokens with row numbers
    ordered_tokens = (
        select(
            Token.token,
            Rfc.num.label('rfc_num'),
            Rfc.title.label('rfc_title'),
            RfcSection.index.label('section_index'),
            RfcSection.page.label('page'),
            RfcLine.line_number,
            RfcLine.abs_line_number,
            TokenPosition.index.label('token_index'),
            TokenPosition.start_position,
            TokenPosition.end_position,
                        func.row_number()
            .over(
                order_by=[
                    Rfc.num,
                    RfcSection.page,
                    RfcSection.index,
                    RfcLine.line_number,
                    TokenPosition.index,
                ]
            )
            .label('row_num'),

        )
        .join(TokenPosition, Token.id == TokenPosition.token_id)
        .join(RfcLine, TokenPosition.line_id == RfcLine.id)
        .join(RfcSection, RfcLine.section_id == RfcSection.id)
        .join(Rfc, RfcSection.rfc_num == Rfc.num)
    )
    return ordered_tokens
