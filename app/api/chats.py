
from fastapi import APIRouter, Path

from pydantic import BaseModel

router = APIRouter()

class Message(BaseModel):
    pass