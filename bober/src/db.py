import os
from functools import wraps
from typing import Callable

from dotenv import load_dotenv
from sqlalchemy import MetaData
from sqlalchemy.orm import Session


def commit(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = next(arg for arg in args if isinstance(arg, Session))
        try:
            result = func(*args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e

    return wrapper


def drop_schema(engine):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)


def get_database_url():
    load_dotenv()
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
    return f"{POSTGRES_SCHEMA}://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
