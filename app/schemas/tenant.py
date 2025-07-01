# Placeholder for Tenant schema 

from pydantic import BaseModel
from typing import Dict, Any, Optional, Union
from datetime import datetime

class BusinessProfileBase(BaseModel):
    name: str
    settings: Optional[Dict[str, Any]] = {}

class BusinessProfileCreate(BusinessProfileBase):
    pass

class BusinessProfileRead(BusinessProfileBase):
    id: int

    class Config:
        orm_mode = True 

class BusinessDocumentBase(BaseModel):
    type: str
    filename: Optional[str] = None
    url: Optional[str] = None
    storage_path: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = {}

class BusinessDocumentCreate(BusinessDocumentBase):
    business_profile_id: int

class BusinessDocumentRead(BusinessDocumentBase):
    id: int
    business_profile_id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True 