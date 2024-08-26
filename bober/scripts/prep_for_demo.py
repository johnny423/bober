from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

from bober.src.db_models import Base
from bober.src.main import get_database_url, drop_schema
from bober.src.phrases.phrases import save_new_phrase
from bober.src.loader import load_examples as _load_examples
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
        # "Avian Carriers",  # todo re-add this after we fix adding non existing tokens
        # "scroll of paper",  # todo re-add this after we fix adding non existing tokens
        "Security Considerations",
        "PROTOCOL DEFINITION",
        "source address",
        # "The internet society",  # todo re-add this after we fix adding non existing tokens
    ]
    for phrase in phrases_to_add:
        logger.info(f"Adding phrase {phrase}")
        save_new_phrase(session, phrase.lower(), phrase)


def add_groups(session):
    groups_to_add = {
        # "Universities": [  # todo looks like a bug but crashes
        #     "UCLA ",
        # ],
        "protocols": [
            "ethernet",
            "http",
            "ip",
            "tcp",
            # "udp",
            # "nfs",
            # "smtp",
            # "nntp",
            # "dns",
        ],
    }

    for group_name, group_items in groups_to_add.items():
        logger.info(f"Adding group {group_name}: {group_items}")
        create_word_group(session, group_name, group_items)


def main():
    session = init_db()
    load_examples(session)
    add_phrases(session)
    add_groups(session)


if __name__ == '__main__':
    main()
