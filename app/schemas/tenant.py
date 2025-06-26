# Placeholder for Tenant schema 

from pydantic import BaseModel
from typing import Dict, Any, Optional

class BusinessProfileBase(BaseModel):
    name: str
    settings: Optional[Dict[str, Any]] = {}

class BusinessProfileCreate(BusinessProfileBase):
    pass

class BusinessProfileRead(BusinessProfileBase):
    id: int

    class Config:
        orm_mode = True 