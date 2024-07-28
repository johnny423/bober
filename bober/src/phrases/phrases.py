from sqlalchemy import func
from sqlalchemy.orm import Session

from bober.src.db import commit
from bober.src.db_models import Phrase, PhraseToken, RfcSection, Token
from bober.src.rfc_ingest.parsing import tokenize


@commit
def save_new_phrase(session: Session, phrase_name: str, phrase: str):
    words = [token for token, _ in tokenize(phrase)]

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


def find_phrase_occurrences(
    session: Session, phrase_name: str
) -> list[RfcSection]:
    phrase = (
        session.query(Phrase)
        .filter(Phrase.phrase_name == phrase_name)
        .one_or_none()
    )
    if not phrase:
        raise ValueError(f"Phrase with name {phrase_name} does not exist.")

    return search_content(session, phrase.content)


def search_content(session: Session, phrase: str) -> list[RfcSection]:
    return (
        session.query(RfcSection)
        .filter(func.to_tsvector('english', RfcSection.content).match(phrase))
        .all()
    )
