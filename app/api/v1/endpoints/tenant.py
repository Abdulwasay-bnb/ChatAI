from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.config import get_db
from app.models.tenant import BusinessProfile, BusinessDocument
from app.schemas.tenant import BusinessProfileCreate, BusinessProfileRead, BusinessDocumentCreate, BusinessDocumentRead
from typing import List, Optional
from app.api.v1.endpoints.auth import get_current_user_from_cookie
from app.models.user import User
import os, shutil, uuid
from fastapi.responses import FileResponse, JSONResponse
import mimetypes
import csv
from app.services.chatbot_service import process_and_store_document
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

def extract_data_from_file(file_path, filetype):
    if filetype == 'pdf' and PdfReader:
        try:
            reader = PdfReader(file_path)
            text = " ".join(page.extract_text() or '' for page in reader.pages)
            return {"text": text[:5000]}  # Limit for preview
        except Exception as e:
            return {"error": str(e)}
    elif filetype == 'csv':
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                rows = [row for _, row in zip(range(20), reader)]  # Preview first 20 rows
            return {"rows": rows}
        except Exception as e:
            return {"error": str(e)}
    return {}

@router.post("/business-document/", response_model=BusinessDocumentRead)
def upload_business_document(
    business_profile_id: int = Form(...),
    type: str = Form(...),
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_cookie)
):
    if not file and not url:
        raise HTTPException(status_code=400, detail="Either file or url must be provided.")
    filename = None
    storage_path = None
    extracted_data = {}
    if file:
        ext = os.path.splitext(file.filename)[1].lower()
        filename = f"{uuid.uuid4().hex}{ext}"
        storage_path = os.path.join(UPLOAD_DIR, filename)
        with open(storage_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Extract data from file (PDF/CSV)
        if ext == '.pdf':
            extracted_data = extract_data_from_file(storage_path, 'pdf')
        elif ext == '.csv':
            extracted_data = extract_data_from_file(storage_path, 'csv')
    if url:
        # TODO: Fetch and extract data from URL if needed
        pass
    doc = BusinessDocument(
        business_profile_id=business_profile_id,
        type=type,
        filename=file.filename if file else None,
        url=url,
        storage_path=storage_path,
        extracted_data=extracted_data
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    # Optionally update BusinessProfile.settings pointer
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == business_profile_id).first()
    if profile:
        if not profile.settings:
            profile.settings = {}
        profile.settings[f"{type}_doc_id"] = doc.id
        db.commit()
    # RAG: Process and store document in Chroma
    process_and_store_document(doc, user.id)
    return doc

@router.get("/business-document/", response_model=List[BusinessDocumentRead])
def list_business_documents(business_profile_id: int, db: Session = Depends(get_db)):
    return db.query(BusinessDocument).filter(BusinessDocument.business_profile_id == business_profile_id).all()

@router.get("/business-document/{doc_id}", response_model=BusinessDocumentRead)
def get_business_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(BusinessDocument).filter(BusinessDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/business-document/{doc_id}")
def delete_business_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(BusinessDocument).filter(BusinessDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # Remove file if exists
    if doc.storage_path and os.path.exists(doc.storage_path):
        os.remove(doc.storage_path)
    db.delete(doc)
    db.commit()
    return {"msg": "Document deleted"}

@router.get("/business-document/{doc_id}/preview")
def preview_business_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(BusinessDocument).filter(BusinessDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # For file: return extracted_data (text/csv preview)
    # For link: TODO: fetch preview if needed
    return JSONResponse(content=doc.extracted_data or {})

@router.get("/business-document/{doc_id}/download")
def download_business_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(BusinessDocument).filter(BusinessDocument.id == doc_id).first()
    if not doc or not doc.storage_path or not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=404, detail="File not found")
    mime, _ = mimetypes.guess_type(doc.storage_path)
    return FileResponse(doc.storage_path, media_type=mime or 'application/octet-stream', filename=doc.filename or os.path.basename(doc.storage_path)) 