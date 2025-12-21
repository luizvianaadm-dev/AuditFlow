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

    # Determine system role based on Job Role Level
    # Level 1 (Sócio) and 2 (Diretor) get Admin access
    system_role = "auditor"
    job_role = db.query(models.JobRole).filter(models.JobRole.id == invite.job_role_id).first()
    if job_role and job_role.level <= 2:
        system_role = "admin"

    new_user = models.User(
        email=invite.email,
        hashed_password=hashed_password,
        role=system_role, 
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


