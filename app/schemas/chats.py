from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatBase(BaseModel):
    user_id: int
    chatbot_id: int
    message: str
    response: Optional[str] = None
    timestamp: Optional[datetime] = None

class ChatCreate(ChatBase):
    pass

class ChatRead(ChatBase):
    id: int

    class Config:
        orm_mode = True 