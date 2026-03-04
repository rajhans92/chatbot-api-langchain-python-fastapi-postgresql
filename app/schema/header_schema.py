from pydantic import BaseModel

class HeaderDetail(BaseModel):
    sessionId: int
    userId: int