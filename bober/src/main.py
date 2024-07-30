import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bober.src.db_models import Base
from bober.src.fe.launch_gui import launch_gui
from bober.src.loader import load_examples

RELOAD_DATA = False

if __name__ == "__main__":
    # todo: move to pydantic
    load_dotenv()

    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
    DATABASE_URL = f"{POSTGRES_SCHEMA}://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(DATABASE_URL)

    Base.metadata.create_all(engine)

    Session = sessionmaker(engine)

    with Session() as session:
        if RELOAD_DATA:
            for tbl in reversed(Base.metadata.sorted_tables):
                session.execute(tbl.delete())
            session.commit()

            load_examples(session)

        launch_gui(session)
