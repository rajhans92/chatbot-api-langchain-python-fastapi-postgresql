from pydentic import BaseModel
from typing import List


class HeaderDetail(BaseModel):
    userId: int
    sessionId: int