from pydantic import BaseModel
from typing import List, Union

class Card(BaseModel):
    uid: int
    value: str
    color: str
    actions: List[Union[str, int]]