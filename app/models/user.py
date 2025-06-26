from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.config import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"))

    business_profile = relationship("BusinessProfile", back_populates="users")
    chatbots = relationship("Chatbot", back_populates="owner")
    chats = relationship("Chat", back_populates="user") 