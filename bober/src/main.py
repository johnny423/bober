import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bober.src.db_models import Base
from bober.src.fe.launch_gui import launch_gui
from bober.src.loader import load_examples
from bober.src.search.rfc_content import load_rfc_content, get_section_absolute_line_query, get_absolute_position

SHOULD_RELOAD_DATA = False


def get_database_uel():
    load_dotenv()
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
    return f"{POSTGRES_SCHEMA}://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"


if __name__ == "__main__":
    database_url = get_database_uel()
    engine = create_engine(database_url)

    Base.metadata.create_all(engine)

    Session = sessionmaker(engine)

    with Session() as session:
        if SHOULD_RELOAD_DATA:
            for tbl in reversed(Base.metadata.sorted_tables):
                session.execute(tbl.delete())
            session.commit()

            load_examples(session)

        launch_gui(session)
        # content = load_rfc_content(session, 1).splitlines()
        #
        # res = get_absolute_position(session, 1, "Questions")
        # for row in res:
        #     print(content[row.line - 1][row.start: row.start + row.length])
