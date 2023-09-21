from sqlalchemy import Boolean, Column, DateTime, Integer, PrimaryKeyConstraint, String

from .base import Base


class TodoORM(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, index=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

    __table_args__ = (PrimaryKeyConstraint("id", "client_id"),)  # Composite primary key
