import os

import fastapi
import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from starlette.middleware.trustedhost import TrustedHostMiddleware

from bober.src.config import get_settings
from bober.src.db_models import Base


def initialize_backend_application() -> fastapi.FastAPI:
    fastapi_app = fastapi.FastAPI()

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in get_settings().security.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=get_settings().security.ALLOWED_HOSTS,
    )

    return fastapi_app


backend_app: fastapi.FastAPI = initialize_backend_application()

if __name__ == "__main__":
    # todo: move to pydantic
    load_dotenv()

    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
    DATABASE_URL = (
        f"{POSTGRES_SCHEMA}://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    engine = create_engine(DATABASE_URL)

    Base.metadata.create_all(engine)

    settings = get_settings()
    uvicorn.run(
        app="main:backend_app",
        host=settings.server.SERVER_HOST,
        port=settings.server.SERVER_PORT,
        reload=settings.server.DEBUG,
        workers=settings.server.SERVER_WORKERS,
    )
