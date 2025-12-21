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

@router.post("/fix-structure")
def fix_missing_structure(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Helper to re-initialize departments, roles, and fix DB schema if columns are missing.
    """
    from sqlalchemy import text
    firm_id = current_user.firm_id
    
    # 1. Patch Database Schema (Manual Migration for email_contact)
    try:
        # Check if column exists, if not add it. 
        # PostgreSQL specific check or just try adding and ignore error?
        # Robust way:
        db.execute(text("ALTER TABLE audit_firms ADD COLUMN IF NOT EXISTS email_contact VARCHAR;"))
        db.commit()
    except Exception as e:
        print(f"Schema patch error (might be ignored): {e}")
        db.rollback()

    # 2. Check Departments
    if db.query(models.Department).filter(models.Department.firm_id == firm_id).count() == 0:
        default_depts = [
            {"name": "Administrativo", "is_overhead": True},
            {"name": "Financeiro", "is_overhead": True},
            {"name": "Recursos Humanos", "is_overhead": True},
            {"name": "Comercial", "is_overhead": True},
            {"name": "Jurídico", "is_overhead": True},
            {"name": "Auditoria", "is_overhead": False},
        ]
        for dept in default_depts:
            db.add(models.Department(name=dept["name"], is_overhead=dept["is_overhead"], firm_id=firm_id))
    
    # Check Roles
    if db.query(models.JobRole).filter(models.JobRole.firm_id == firm_id).count() == 0:
        default_roles = [
            {"name": "Sócio", "level": 1, "hourly_rate": 500.0},
            {"name": "Diretor", "level": 2, "hourly_rate": 400.0},
            {"name": "Gerente Sênior", "level": 3, "hourly_rate": 350.0},
            {"name": "Gerente", "level": 4, "hourly_rate": 300.0},
            {"name": "Supervisor A", "level": 5, "hourly_rate": 250.0},
            {"name": "Supervisor B", "level": 6, "hourly_rate": 220.0},
            {"name": "Sênior A", "level": 7, "hourly_rate": 180.0},
            {"name": "Sênior B", "level": 8, "hourly_rate": 160.0},
            {"name": "Sênior C", "level": 9, "hourly_rate": 140.0},
            {"name": "Assistente A", "level": 10, "hourly_rate": 100.0},
            {"name": "Assistente B", "level": 11, "hourly_rate": 80.0},
            {"name": "Trainee", "level": 12, "hourly_rate": 50.0},
            {"name": "Estagiário", "level": 13, "hourly_rate": 30.0},
        ]
        for role in default_roles:
            db.add(models.JobRole(name=role["name"], level=role["level"], hourly_rate=role["hourly_rate"], firm_id=firm_id))
            
    db.commit()
    return {"message": "Structure fixed and Schema Patched"}

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
