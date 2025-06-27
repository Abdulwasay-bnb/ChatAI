from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.config import get_db
from models.tenant import BusinessProfile
from schemas.tenant import BusinessProfileCreate, BusinessProfileRead
from typing import List
from api.v1.endpoints.auth import get_current_user_from_cookie
from models.user import User

router = APIRouter()

@router.post("/", response_model=BusinessProfileRead)
def create_business_profile(profile: BusinessProfileCreate, db: Session = Depends(get_db)):
    db_profile = BusinessProfile(name=profile.name, settings=profile.settings)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/", response_model=List[BusinessProfileRead])
def list_business_profiles(db: Session = Depends(get_db)):
    return db.query(BusinessProfile).all()

@router.get("/{profile_id}", response_model=BusinessProfileRead)
def get_business_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    return profile

@router.put("/{profile_id}", response_model=BusinessProfileRead)
def update_business_profile(profile_id: int, profile: BusinessProfileCreate, db: Session = Depends(get_db)):
    db_profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    db_profile.name = profile.name
    db_profile.settings = profile.settings
    db.commit()
    db.refresh(db_profile)
    return db_profile

def admin_required(user: User = Depends(get_current_user_from_cookie)):
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.delete("/{profile_id}")
def delete_business_profile_by_admin(profile_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    db_profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    db.delete(db_profile)
    db.commit()
    return {"msg": "Business profile deleted"} 