from typing import Generic, List, Optional, Type, TypeVar

from models import TodoORM, User
from pydantic import BaseModel
from schemas.todos import TodoCreate, TodoUpdate
from schemas.users import UserCreate, UserUpdate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")  # database model type
CreateSchemaType = TypeVar(
    "CreateSchemaType", bound=BaseModel
)  # Pydantic create schema type
UpdateSchemaType = TypeVar(
    "UpdateSchemaType", bound=BaseModel
)  # Pydantic update schema type


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, *, id: int, client_id: str) -> Optional[ModelType]:
        return (
            db.query(self.model)
            .filter(self.model.id == id, self.model.client_id == client_id)
            .first()
        )

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        obj_data = obj_in.dict()
        for attr, value in obj_data.items():
            if hasattr(db_obj, attr):
                setattr(db_obj, attr, value)
        try:
            db.commit()
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    def patch(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        obj_data = obj_in.dict(exclude_unset=True)
        for attr, value in obj_data.items():
            if hasattr(db_obj, attr):
                setattr(db_obj, attr, value)
        try:
            db.commit()
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    def delete(self, db: Session, *, id: int, client_id: str) -> ModelType:
        obj = (
            db.query(self.model)
            .filter(self.model.id == id, self.model.client_id == client_id)
            .first()
        )
        db.delete(obj)
        try:
            db.commit()
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    pass


class CRUDTodo(CRUDBase[TodoORM, TodoCreate, TodoUpdate]):
    pass
