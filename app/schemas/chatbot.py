from pydantic import BaseModel
from typing import Dict, Any, Optional

class ChatbotBase(BaseModel):
    name: str
    prompt: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {}
    owner_id: Optional[int] = None
    business_profile_id: Optional[int] = None

class ChatbotCreate(ChatbotBase):
    pass

class ChatbotRead(ChatbotBase):
    id: int

    class Config:
        orm_mode = True

class ChatbotSuggestionBase(BaseModel):
    suggestions: Dict[str, str]

class ChatbotSuggestionCreate(ChatbotSuggestionBase):
    chatbot_id: int

class ChatbotSuggestionOut(ChatbotSuggestionBase):
    id: int
    chatbot_id: int
    class Config:
        orm_mode = True 