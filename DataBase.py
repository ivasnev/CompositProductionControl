from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("mysql://root:1234@localhost:3306 ", echo=True)


def get_session():
    return Session(engine)
