from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import NullPool

from config import settings

nldb_url = (
    f"postgresql+psycopg2://{settings.db_username}:{settings.db_password}@"
    f"{settings.db_host}:5432/{settings.db_name}"
)

engine = create_engine(nldb_url, poolclass=NullPool, future=True)

SessionFactory = sessionmaker(autocommit=False, bind=engine, future=True)

Base = declarative_base()


def get_session() -> Session:
    return SessionFactory()
