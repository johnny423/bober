from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bober.src.db import get_database_url
from bober.src.db_models import Base
from bober.src.fe.launch_gui import launch_gui

if __name__ == "__main__":
    database_url = get_database_url()
    engine = create_engine(database_url)

    Base.metadata.create_all(engine)

    Session = sessionmaker(engine)

    with Session() as session:
        launch_gui(session)
