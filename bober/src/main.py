import os

from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

from bober.src.db_models import Base
from bober.src.fe.launch_gui import launch_gui
from bober.src.loader import load_examples

SHOULD_RELOAD_DATA = False
SHOULD_RELOAD_SCHEMA = False


def get_database_uel():
    load_dotenv()
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
    return f"{POSTGRES_SCHEMA}://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"


def drop_schema(engine):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)


if __name__ == "__main__":
    database_url = get_database_uel()
    engine = create_engine(database_url)
    if SHOULD_RELOAD_SCHEMA:
        logger.info("Dropping the schema per user request")
        drop_schema(engine)

    Base.metadata.create_all(engine)

    Session = sessionmaker(engine)

    with Session() as session:
        if SHOULD_RELOAD_DATA:
            logger.info("Start reloading the data")

            logger.info("Start deleting existing tables")
            for tbl in reversed(Base.metadata.sorted_tables):
                session.execute(tbl.delete())
            session.commit()
            logger.info("Ended deleting existing tables")

            logger.info("Start loading examples")
            load_examples(session)
            logger.info("Ended loading examples")

        launch_gui(session)
