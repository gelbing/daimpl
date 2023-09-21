# profiles/routes.py
from typing import List

from crud import CRUDTodo
from engine import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import TodoORM as TodoORM
from schemas import Todo, TodoCreate, TodoUpdate
from sqlalchemy.orm import Session

router = APIRouter()

crud_todo = CRUDTodo(TodoORM)


#     return graph_data
@router.get("/todo", tags=["todos"], response_model=List[Todo])
# trunk-ignore(ruff/B008)
async def get_all_todos(db: Session = Depends(get_db)) -> List[Todo]:
    todos = crud_todo.get_multi(db=db)
    if todos is None:
        raise HTTPException(status_code=404, detail="No Todos Found")
    return todos


@router.get("/todo/{client_id}/{todo_id}", tags=["todos"], response_model=Todo)
async def get_todo_by_id(
    client_id: str, todo_id: int, db: Session = Depends(get_db)
) -> Todo:
    db_todo = crud_todo.get(db, id=todo_id, client_id=client_id)

    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo


@router.post("/todo", tags=["todos"], response_model=Todo)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)) -> Todo:
    db_todo = crud_todo.create(db, obj_in=todo)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Error creating todo")
    return db_todo


@router.post("/todo/{client_id}/{todo_id}", tags=["todos"], response_model=Todo)
async def update_todo(
    client_id: str, todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)
) -> Todo:
    db_todo = crud_todo.get(db, id=todo_id, client_id=client_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud_todo.update(db, db_obj=db_todo, obj_in=todo)


@router.delete("/todo/{client_id}/{todo_id}", tags=["todos"], response_model=Todo)
async def delete_todo(
    client_id: str, todo_id: int, db: Session = Depends(get_db)
) -> Todo:
    db_todo = crud_todo.get(db, id=todo_id, client_id=client_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud_todo.delete(db, id=todo_id, client_id=client_id)
