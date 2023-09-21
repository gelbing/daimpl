from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str = Field(..., description="Name of the user")
    email: str = Field(..., description="Email of the user")


class UserUpdate(UserBase):
    name: Optional[str] = Field(None, description="Name of the user")
    email: Optional[str] = Field(None, description="Email of the user")


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int = Field(..., description="The unique todo-id")

    class Config:
        orm_mode = True
