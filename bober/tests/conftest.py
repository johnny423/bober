import os

import psycopg2
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

from bober.src.db_models import Base


@pytest.fixture(scope='session')
def base_db_url():
    load_dotenv()

    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
    DATABASE_URL = f"{POSTGRES_SCHEMA}://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
    return DATABASE_URL


@pytest.fixture(scope='session')
def test_db_url():
    load_dotenv()

    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
    DATABASE_URL = f"{POSTGRES_SCHEMA}://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/test"
    return DATABASE_URL


@pytest.fixture(scope="session", autouse=True)
def create_test_database(base_db_url):
    # Connect to the default database to create the test database
    conn = psycopg2.connect(base_db_url)
    conn.autocommit = True
    cur = conn.cursor()

    # Drop the test database if it already exists and create a new one
    cur.execute(f"DROP DATABASE IF EXISTS test")
    cur.execute(f"CREATE DATABASE test")
    cur.close()
    conn.close()


@pytest.fixture(scope='function')
def db_session(test_db_url):
    engine = create_engine(test_db_url)
    Base.metadata.bind = engine

    # create table if not existing
    Base.metadata.create_all(engine)

    # create session
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    try:
        yield session
    finally:
        # Clear the tables
        meta = MetaData()
        meta.reflect(bind=engine)
        with engine.connect() as conn:
            for table in reversed(meta.sorted_tables):
                conn.execute(table.delete())
        session.close()
        Session.remove()
