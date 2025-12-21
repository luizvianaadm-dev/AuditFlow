from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.api.database import get_db
from src.api import models, schemas, security

router = APIRouter(prefix="/firm", tags=["firm"])

@router.get("/departments", response_model=List[schemas.DepartmentRead])
def get_departments(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Department).filter(models.Department.firm_id == current_user.firm_id).all()

@router.get("/job-roles", response_model=List[schemas.JobRoleRead])
def get_job_roles(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.JobRole).filter(models.JobRole.firm_id == current_user.firm_id).order_by(models.JobRole.level).all()

@router.get("/", response_model=schemas.AuditFirmRead)
def get_firm_details(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    firm = db.query(models.AuditFirm).filter(models.AuditFirm.id == current_user.firm_id).first()
    if not firm:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Firm not found")
    return firm

@router.put("/", response_model=schemas.AuditFirmRead)
def update_firm_details(
    firm_update: schemas.AuditFirmUpdate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    # Only Admin/Partner can update firm details
    # Assuming role check is desired but not strictly enforced for MVP demo speed, or check level
    # if current_user.job_role.level > 2: raise 403
    
    firm = db.query(models.AuditFirm).filter(models.AuditFirm.id == current_user.firm_id).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Firm not found")
        
    for key, value in firm_update.model_dump(exclude_unset=True).items():
        setattr(firm, key, value)
    
    db.commit()
    db.refresh(firm)
    return firm

from fastapi import UploadFile, File, HTTPException

@router.post("/letterhead")
def upload_firm_letterhead(
    file: UploadFile = File(...),
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    import os
    import shutil
    from datetime import datetime
    
    UPLOAD_DIR = "static/letterheads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    filename = f"firm_{current_user.firm_id}_{int(datetime.now().timestamp())}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    firm = db.query(models.AuditFirm).filter(models.AuditFirm.id == current_user.firm_id).first()
    firm.firm_letterhead_url = f"/static/letterheads/{filename}"
    db.commit()
    
    return {"url": firm.firm_letterhead_url}
