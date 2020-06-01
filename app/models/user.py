# database playground
# from typing import List
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    # different class to never have the plain-text password accessible
    password: str

class User(UserBase):
    # uid: str
    id: int
    # is_active: bool
    # current_game: str = ''

    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str

