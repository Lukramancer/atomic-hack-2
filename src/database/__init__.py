from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import URL

from .models import *


def main(database_driver: str, database_host: str, database_port: int, database_username: str, database_password: str, database_name: str):
    database_url = URL.create(
        drivername=database_driver,
        username=database_username,
        password=database_password,
        host=database_host,
        database=database_name,
        port=database_port
    )
    engine = create_engine(database_url)
    make_db_session = sessionmaker(autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    return make_db_session()


def register_user_if_not_exists(database_session: Session, user_id: int):
    user = database_session.query(User).get(user_id)
    if user is None:
        user = User(id=user_id)
        database_session.add(user)
        database_session.commit()
    return user
