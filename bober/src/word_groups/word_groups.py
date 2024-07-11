from sqlalchemy.orm import Session

from bober.src.db import commit
from bober.src.db_models import TokenGroup, Token, TokenToGroup


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
    group = session.query(TokenGroup).filter_by(group_name=group_name).first()
    if not group:
        raise ValueError(f"Group '{group_name}' does not exist")

    # Get existing tokens
    # currently ignoring non-existing tokens!
    existing_tokens = session.query(Token).filter(Token.token.in_(words)).all()
    existing_token_dict = {token.token: token for token in existing_tokens}

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

    # Create new associations
    new_associations = [
        TokenToGroup(token=existing_token_dict[word], group=group)
        for word in words
        if (existing_token_dict[word].id, group.id)
        not in existing_association_set
    ]
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
