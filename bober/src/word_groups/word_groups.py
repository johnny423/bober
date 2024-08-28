from sqlalchemy.orm import Session, selectinload

from bober.src.db import commit
from bober.src.db_models import Token, TokenGroup, TokenToGroup
from bober.src.parsing.parsed_types import STEMMER


@commit
def create_word_group(
    session: Session, group_name: str, words: list[str]
) -> TokenGroup:
    new_group = TokenGroup(group_name=group_name)
    session.add(new_group)

    if words:
        add_words_to_group(session, group_name, words)

    return new_group


@commit
def add_words_to_group(
    session: Session, group_name: str, words: list[str]
) -> None:
    words = [word.lower() for word in words]
    group = session.query(TokenGroup).filter_by(group_name=group_name).first()
    if not group:
        raise ValueError(f"Group '{group_name}' does not exist")

    existing_tokens = session.query(Token).filter(Token.token.in_(words)).all()
    existing_token_dict = {token.token: token for token in existing_tokens}

    new_tokens = []
    for word in words:
        if word  in existing_token_dict:
            continue

        new_token = Token(token=word, stem=STEMMER.stem(word))
        new_tokens.append(new_token)
        existing_token_dict[word] = new_token

    session.add_all(new_tokens)
    session.flush()

    # Get existing associations
    existing_associations = (
        session.query(TokenToGroup)
        .filter(
            TokenToGroup.group == group,
            TokenToGroup.token_id.in_(
                [token.id for token in existing_token_dict.values()]
            ),
        )
        .all()
    )
    existing_association_set = {
        (assoc.token_id, assoc.group_id) for assoc in existing_associations
    }

    new_associations = []
    for word in words:
        if (
            existing_token_dict[word].id,
            group.id,
        ) not in existing_association_set:
            new_associations.append(
                TokenToGroup(token=existing_token_dict[word], group=group)
            )

    session.add_all(new_associations)


@commit
def remove_words_from_group(
    session: Session, group_name: str, words: list[str]
) -> None:
    group = session.query(TokenGroup).filter_by(group_name=group_name).first()
    if not group:
        raise ValueError(f"Group '{group_name}' does not exist")

    # Get tokens for the words
    tokens = session.query(Token).filter(Token.token.in_(words)).all()
    token_ids = [token.id for token in tokens]

    # Delete associations in batch
    session.query(TokenToGroup).filter(
        TokenToGroup.group == group, TokenToGroup.token_id.in_(token_ids)
    ).delete(synchronize_session=False)


def list_groups(session):
    return session.query(TokenGroup).all()


def list_words_in_group(session, group_name) -> list[str]:
    group = (
        session.query(TokenGroup)
        .options(selectinload(TokenGroup.tokens))
        .filter(TokenGroup.group_name == group_name)
        .one_or_none()
    )
    if not group:
        return []

    return [t.token.token for t in group.tokens]
