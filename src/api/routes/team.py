from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from src.api.database import get_db
from src.api import models, schemas, security
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/firm",
    tags=["team"]
)

@router.get("/team", response_model=List[schemas.UserRead])
def get_firm_team(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.User).filter(models.User.firm_id == current_user.firm_id).all()

@router.post("/team/invite", response_model=schemas.UserRead)
def invite_user(
    invite: schemas.UserInvite,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Only admin/partners can invite (logic optional for MVP)
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can invite members")

    existing = db.query(models.User).filter(models.User.email == invite.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = security.get_password_hash(invite.password)

    new_user = models.User(
        email=invite.email,
        hashed_password=hashed_password,
        role="auditor", # Force "auditor" access level for now, actual role is in job_role
        firm_id=current_user.firm_id,
        
        # Profile Data
        cpf=invite.cpf,
        phone=invite.phone,
        birthday=invite.birthday,
        admission_date=invite.admission_date,
        
        # Structure
        department_id=invite.department_id,
        job_role_id=invite.job_role_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/letterhead", status_code=status.HTTP_201_CREATED)
def upload_firm_letterhead(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Uploads the Audit Firm's standard letterhead (Timbrado da Auditoria).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update firm settings")

    # 1. Validate File Type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image (PNG, JPG)")

    # 2. Save File
    import os
    import shutil
    from datetime import datetime
    
    UPLOAD_DIR = "static/letterheads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    filename = f"firm_{current_user.firm_id}_{int(datetime.now().timestamp())}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. Update Database
    firm = db.query(models.AuditFirm).filter(models.AuditFirm.id == current_user.firm_id).first()
    firm.firm_letterhead_url = f"/static/letterheads/{filename}"
    db.commit()

    return {"message": "Firm Letterhead uploaded successfully", "url": firm.firm_letterhead_url}
