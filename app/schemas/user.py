from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False
    business_profile_id: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: str

    class Config:
        orm_mode = True 