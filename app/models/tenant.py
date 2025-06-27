from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.core.config import Base

class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    settings = Column(JSON, default={})

    users = relationship("User", back_populates="business_profile")
    chatbots = relationship("Chatbot", back_populates="business_profile") 