from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.config import get_db
from models.chatbot import Chatbot
from models.user import User
from schemas.chatbot import ChatbotCreate, ChatbotRead
from typing import List
from core import config
from pydantic import BaseModel
import json
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

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
    db_chatbot = Chatbot(**chatbot.dict())
    db.add(db_chatbot)
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot

@router.get("/", response_model=List[ChatbotRead])
def list_chatbots(db: Session = Depends(get_db)):
    return db.query(Chatbot).all()

@router.get("/{chatbot_id}", response_model=ChatbotRead)
def get_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return chatbot

@router.put("/{chatbot_id}", response_model=ChatbotRead)
def update_chatbot(chatbot_id: int, chatbot: ChatbotCreate, db: Session = Depends(get_db)):
    db_chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not db_chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    for key, value in chatbot.dict().items():
        setattr(db_chatbot, key, value)
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot

class ChatRequest(BaseModel):
    prompt: str
    chatbot_id: int
    user_id: int

@router.post("/chat")
def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db)):
    pipe = config.PIPE
    llm_model = config.LLM_MODEL
    prompt = request.prompt
    chatbot = db.query(Chatbot).filter(Chatbot.id == request.chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    # Optionally, add chatbot.prompt or settings to the prompt
    full_prompt = f"{chatbot.prompt}\n{prompt}" if chatbot.prompt else prompt
    try:
        response = pipe(
            model=llm_model,
            messages=[{'role': 'user', 'content': full_prompt}]
        )
        if hasattr(response, 'message') and hasattr(response.message, 'content'):
            content = response.message.content
        elif isinstance(response, dict) and 'message' in response:
            content = response['message']['content']
        else:
            content = str(response)
        try:
            return json.loads(content)
        except Exception:
            return {"response": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 