from fastapi import APIRouter, Depends, HTTPException, Request, Security
from sqlalchemy.orm import Session
from app.core.config import get_db
from app.models.chatbot import Chatbot
from app.models.user import User
from app.schemas.chatbot import ChatbotCreate, ChatbotRead
from typing import List
from app.core import config
from pydantic import BaseModel
import json
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from app.api.v1.endpoints.auth import get_current_user_from_cookie
from app.services.chatbot_service import ChatbotService

router = APIRouter()

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), '../../../templates'))

@router.get("/view", response_class=HTMLResponse)
def chatbot_view(user_id: int, request: Request):
    # For demo, just render a simple chat UI. You can expand this to load chatbot settings, etc.
    return templates.TemplateResponse("chatbot_view.html", {"request": request, "user_id": user_id})

@router.get("/embed/{user_id}")
def get_embed_link(user_id: int, request: Request, db: Session = Depends(get_db)):
    # Return a JS snippet link filtered by user
    base_url = str(request.base_url).rstrip("/")
    return {"embed_link": f"{base_url}/static/js/embed.js?user_id={user_id}"}

@router.post("/", response_model=ChatbotRead)
def create_chatbot(chatbot: ChatbotCreate, db: Session = Depends(get_db)):
    return ChatbotService.create_chatbot(chatbot, db)

@router.get("/", response_model=List[ChatbotRead])
def list_chatbots(business_profile_id: int = None, db: Session = Depends(get_db)):
    return ChatbotService.list_chatbots(business_profile_id, db)

@router.get("/{chatbot_id}", response_model=ChatbotRead)
def get_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    return ChatbotService.get_chatbot(chatbot_id, db)

@router.put("/{chatbot_id}", response_model=ChatbotRead)
def update_chatbot(chatbot_id: int, chatbot: ChatbotCreate, db: Session = Depends(get_db)):
    return ChatbotService.update_chatbot(chatbot_id, chatbot, db)

class ChatRequest(BaseModel):
    prompt: str
    chatbot_id: int
    user_id: int

@router.post("/chat")
def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db)):
    return ChatbotService.chat_with_bot(request.chatbot_id, request.prompt, request.user_id, db)

def admin_required(user: User = Depends(get_current_user_from_cookie)):
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.delete("/{chatbot_id}")
def delete_chatbot_by_admin(chatbot_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    return ChatbotService.delete_chatbot(chatbot_id, db) 