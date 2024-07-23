import os
from pprint import pprint

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bober.src.db_models import Base
from bober.src.loader import load_examples
from bober.src.search.search_rfc import search_rfcs, SearchRFCQuery
from bober.src.fe.launch_gui import launch_gui

# from bober.src.phrases import save_new_phrase, find_phrase_occurrences
# from bober.src.rfc_search.search_rfc import search_rfcs, SearchRFCQuery

# def initialize_backend_application() -> fastapi.FastAPI:
#     fastapi_app = fastapi.FastAPI()
#
#     fastapi_app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[
#             str(origin)
#             for origin in get_settings().security.BACKEND_CORS_ORIGINS
#         ],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )
#
#     fastapi_app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=get_settings().security.ALLOWED_HOSTS,
#     )
#
#     return fastapi_app
#
#
# backend_app: fastapi.FastAPI = initialize_backend_application()

# settings = get_settings()
# uvicorn.run(
#     app="main:backend_app",
#     host=settings.server.SERVER_HOST,
#     port=settings.server.SERVER_PORT,
#     reload=settings.server.DEBUG,
#     workers=settings.server.SERVER_WORKERS,
# )

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
        for tbl in reversed(Base.metadata.sorted_tables):
            session.execute(tbl.delete())
        session.commit()

        load_examples(session)
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
