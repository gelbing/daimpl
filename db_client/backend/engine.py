import os
import time
from contextlib import contextmanager

from models.base import Base
from sqlalchemy import create_engine, exc, text
from sqlalchemy.orm import sessionmaker

pg_host = os.environ.get("POSTGRES_HOST", "localhost")
pg_port = os.environ.get("POSTGRES_PORT", "5432")
pg_user = os.environ.get("POSTGRES_USER", "postgres")
pg_password = os.environ.get("POSTGRES_PASSWORD", "postgres")

engine = create_engine(f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}")

while True:
    try:
        with engine.connect() as connection:
            break
    except exc.SQLAlchemyError:
        print("PostgreSQL is not available yet - sleeping")
        time.sleep(1)

print("PostgreSQL is available - proceeding")

# Create tables
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# For use with FastAPI's dependency injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# For use with the `with` statement
@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
