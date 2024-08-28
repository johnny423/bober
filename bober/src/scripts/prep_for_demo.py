from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bober.src.db import drop_schema, get_database_url
from bober.src.db_models import Base
from bober.src.phrases.phrases import save_new_phrase
from bober.src.scripts.loader import load_examples as _load_examples
from bober.src.word_groups.word_groups import create_word_group


def init_db():
    database_url = get_database_url()
    engine = create_engine(database_url)

    logger.info("Dropping schema")
    drop_schema(engine)

    logger.info("Creating database")
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()


def load_examples(session):
    logger.info("Loading examples")
    _load_examples(session)


def add_phrases(session):
    phrases_to_add = [
        "coffee pot",
        "avian carriers",
        "scroll of paper",
        "security considerations",
        "protocol definition",
        "source address",
        "the internet society",
        "sun microsystems",
    ]
    for phrase in phrases_to_add:
        logger.info(f"Adding phrase {phrase.lower()}")
        save_new_phrase(session, phrase.lower(), phrase.lower())


def add_groups(session):
    groups_to_add = {
        "Universities": [
            "UCLA",
            "DEC",
            "MIT",
            "SRI",
            "Stanford",
            "Bucknell",
        ],
        "protocols": [
            "ethernet",
            "http",
            "ip",
            "tcp",
            "UDP",
            "nfs",
            "SMTP",
            "NNTP",
            "dns",
        ],
        "types": [
            "avian",
        ]
    }

    for group_name, group_items in groups_to_add.items():
        lower_group_name = group_name.lower()
        lower_group_items = [x.lower() for x in group_items]
        logger.info(f"Adding group {lower_group_name}: {lower_group_items}")
        create_word_group(session, lower_group_name, lower_group_items)


def main():
    session = init_db()
    load_examples(session)
    add_phrases(session)
    add_groups(session)


if __name__ == '__main__':
    main()
