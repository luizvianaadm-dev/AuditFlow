from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from src.api.services.ingestion import TrialBalanceIngestion
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
    existing = db.query(models.AccountMapping).filter(
        models.AccountMapping.firm_id == current_user.firm_id,
        models.AccountMapping.client_description == mapping.client_description
    ).first()

    if existing:
        existing.standard_account_id = mapping.standard_account_id
        db.commit()
        db.refresh(existing)
        return existing
    else:
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

@router.post("/upload-trial-balance", response_model=List[str])
def analyze_trial_balance(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Parses a Trial Balance (CSV/Excel) and returns a list of account descriptions
    that are NOT yet mapped for this firm.
    """
    try:
        df = TrialBalanceIngestion.read_file(file)
        result = TrialBalanceIngestion.validate_and_parse(df)

        if not result["valid"]:
             raise HTTPException(status_code=400, detail=f"Invalid file structure: {', '.join(result['errors'])}")

        unique_accounts = result["unique_accounts"]

        # Get existing mappings for firm
        existing_mappings = db.query(models.AccountMapping.client_description).filter(
            models.AccountMapping.firm_id == current_user.firm_id
        ).all()
        mapped_set = {m[0] for m in existing_mappings}

        # Filter unmapped
        unmapped = [acc for acc in unique_accounts if acc not in mapped_set]
        return unmapped

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.post("/bulk-map", status_code=status.HTTP_201_CREATED)
def bulk_create_mapping(
    mappings: List[schemas.AccountMappingBase],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    count = 0
    for mapping in mappings:
        # Check standard account existence (optimization: cache IDs)
        # For simplicity, just proceeding. FK constraint will fail if invalid.

        existing = db.query(models.AccountMapping).filter(
            models.AccountMapping.firm_id == current_user.firm_id,
            models.AccountMapping.client_description == mapping.client_description
        ).first()

        if existing:
            existing.standard_account_id = mapping.standard_account_id
        else:
            new_mapping = models.AccountMapping(
                firm_id=current_user.firm_id,
                client_description=mapping.client_description,
                standard_account_id=mapping.standard_account_id
            )
            db.add(new_mapping)
        count += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to save mappings: {str(e)}")

    return {"message": f"Successfully processed {count} mappings"}
