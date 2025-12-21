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
