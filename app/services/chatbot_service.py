from sqlalchemy.orm import Session
from models.chatbot import Chatbot
from schemas.chatbot import ChatbotCreate
from core import config
from fastapi import HTTPException
import json

class ChatbotService:
    @staticmethod
    def create_chatbot(chatbot_data: ChatbotCreate, db: Session) -> Chatbot:
        db_chatbot = Chatbot(**chatbot_data.dict())
        db.add(db_chatbot)
        db.commit()
        db.refresh(db_chatbot)
        return db_chatbot

    @staticmethod
    def list_chatbots(business_profile_id: int, db: Session):
        if business_profile_id is None:
            return []
        return db.query(Chatbot).filter(Chatbot.business_profile_id == business_profile_id).all()

    @staticmethod
    def get_chatbot(chatbot_id: int, db: Session) -> Chatbot:
        chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        if not chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        return chatbot

    @staticmethod
    def update_chatbot(chatbot_id: int, chatbot_data: ChatbotCreate, db: Session) -> Chatbot:
        db_chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        if not db_chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        for key, value in chatbot_data.dict().items():
            setattr(db_chatbot, key, value)
        db.commit()
        db.refresh(db_chatbot)
        return db_chatbot

    @staticmethod
    def delete_chatbot(chatbot_id: int, db: Session):
        db_chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        if not db_chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        db.delete(db_chatbot)
        db.commit()
        return {"msg": "Chatbot deleted"}

    @staticmethod
    def chat_with_bot(chatbot_id: int, user_prompt: str, user_id: int, db: Session):
        pipe = config.PIPE
        llm_model = config.LLM_MODEL
        chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
        if not chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        # System role: define the bot's role and context
        system_message = chatbot.prompt or "You are a helpful AI assistant."
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        try:
            response = pipe(
                model=llm_model,
                messages=messages
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