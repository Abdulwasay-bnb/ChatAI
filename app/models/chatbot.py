from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.config import Base

class Chatbot(Base):
    __tablename__ = "chatbots"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    prompt = Column(String(2048))
    settings = Column(JSON, default={})
    owner_id = Column(Integer, ForeignKey("users.id"))
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"))

    owner = relationship("User", back_populates="chatbots")
    business_profile = relationship("BusinessProfile", back_populates="chatbots")
    chats = relationship("Chat", back_populates="chatbot") 