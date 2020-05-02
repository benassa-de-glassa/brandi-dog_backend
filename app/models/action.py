from pydantic import BaseModel
from typing import Union, List, Optional

from .card import Card 

class Action(BaseModel):
    card: Card
    action: Union[str, int]
    mid: int
    mid_2: Optional[int]
    pid_2: Optional[str]