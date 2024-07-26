import os
from pprint import pprint

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bober.src.db_models import Base
from bober.src.loader import load_examples
from bober.src.search.search_rfc import search_rfcs, SearchRFCQuery
from bober.src.fe.launch_gui import launch_gui

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
        # reload data and tables
        # for tbl in reversed(Base.metadata.sorted_tables):
        #     session.execute(tbl.delete())
        # session.commit()

        # load_examples(session)
        launch_gui(session)

        # select content
        # content = fetch_rfc_sections(session, 2324)
        # text = rebuild_content(content)
        # print(text)

        # search_rfcs
        r = search_rfcs(session, SearchRFCQuery(tokens=["coffee"]))
        pprint(r)

        # # phrase
        # save_new_phrase(session, "xxx", "espresso machines")
        # a = find_phrase_occurrences(session, "xxx")
        # print(a[0].content)
        #
