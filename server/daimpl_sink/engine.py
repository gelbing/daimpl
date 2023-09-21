import os
import time
from contextlib import contextmanager

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import declarative_base, sessionmaker

pg_host = os.environ.get("POSTGRES_HOST")
pg_port = os.environ.get("POSTGRES_PORT")
pg_user = os.environ.get("POSTGRES_USER")
pg_password = os.environ.get("POSTGRES_PASSWORD")

Base = declarative_base()
engine = create_engine(f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}")

while True:
    try:
        with engine.connect() as connection:
            break
    except exc.SQLAlchemyError:
        print("Server PostgreSQL is not available yet - sleeping")
        time.sleep(1)

print("PostgreSQL is available - proceeding")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@contextmanager
def get_db():
    """Create a new database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
