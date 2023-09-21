# profiles/routes.py
from typing import List

from crud import CRUDUser
from engine import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import User as UserORM
from schemas import User, UserCreate, UserUpdate
from sqlalchemy.orm import Session

router = APIRouter()

crud_user = CRUDUser(UserORM)


@router.get("/user", tags=["users"], response_model=List[User])
async def get_all_users(db: Session = Depends(get_db)) -> List[User]:
    users = crud_user.get_multi(db=db)
    if users is None:
        raise HTTPException(status_code=404, detail="Users not found")
    return users


@router.get("/user/{user_id}", tags=["users"], response_model=User)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)) -> User:
    db_user = crud_user.get(db, id=user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/user", tags=["users"], response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
    db_user = crud_user.create(db, obj_in=user)
    if not db_user:
        raise HTTPException(status_code=404, detail="Error creating user")
    return db_user


@router.post("/user/{user_id}", tags=["users"], response_model=User)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
) -> User:
    db_user = crud_user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_user.update(db, db_obj=db_user, obj_in=user)


@router.delete("/user/{user_id}", tags=["users"], response_model=User)
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> User:
    db_user = crud_user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_user.delete(db, id=user_id)
