from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    PrimaryKeyConstraint,
    Sequence,
    String,
)
from sqlalchemy.sql import func

from .base import Base


class TodoORM(Base):
    __tablename__ = "todos"

    id = Column(Integer, Sequence("todos_id_seq"), primary_key=True, autoincrement=True)
    client_id = Column(
        String, primary_key=True, index=True
    )  # added client_id as a primary key
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (PrimaryKeyConstraint("id", "client_id"),)  # Composite primary key
