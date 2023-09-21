from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    title: str = Field(..., description="Title of the todo")
    description: str = Field(default=None, description="Description of the todo")
    completed: bool = Field(
        default=False, description="Whether the todo is completed or not"
    )


class TodoCreate(TodoBase):
    id: int = Field(..., description="ID of the todo")
    client_id: str = Field(..., description="Client ID of the user")
    created_at: datetime
    updated_at: datetime
    pass


class TodoUpdate(TodoBase):
    updated_at: datetime
    pass


class Todo(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: str
    created_at: datetime
    updated_at: datetime
