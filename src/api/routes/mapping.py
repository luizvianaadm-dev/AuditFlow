from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/mapping",
    tags=["mapping"]
)

@router.get("/standard-accounts", response_model=List[schemas.StandardAccountRead])
def list_standard_accounts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.StandardAccount).all()

@router.post("/map", response_model=schemas.AccountMappingRead)
def create_mapping(
    mapping: schemas.AccountMappingBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if standard account exists
    std_account = db.query(models.StandardAccount).filter(models.StandardAccount.id == mapping.standard_account_id).first()
    if not std_account:
        raise HTTPException(status_code=404, detail="Standard Account not found")

    # Create or Update Mapping for this firm
    # Check if already mapped
    existing = db.query(models.AccountMapping).filter(
        models.AccountMapping.firm_id == current_user.firm_id,
        models.AccountMapping.client_description == mapping.client_description
    ).first()

    if existing:
        # Update
        existing.standard_account_id = mapping.standard_account_id
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create
        new_mapping = models.AccountMapping(
            firm_id=current_user.firm_id,
            client_description=mapping.client_description,
            standard_account_id=mapping.standard_account_id
        )
        db.add(new_mapping)
        db.commit()
        db.refresh(new_mapping)
        return new_mapping

@router.get("/firm-mappings", response_model=List[schemas.AccountMappingRead])
def list_firm_mappings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.AccountMapping).filter(
        models.AccountMapping.firm_id == current_user.firm_id
    ).all()
