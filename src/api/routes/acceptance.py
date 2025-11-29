from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/clients",
    tags=["acceptance"]
)

@router.get("/{client_id}/acceptance")
def get_client_acceptance(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Assuming we might store status in a future column or just return static for MVP
    # Ideally we'd have an Acceptance table.
    # For now, let's just return a placeholder structure
    return {
        "status": "pending", # pending, approved, rejected
        "checklist": {
            "independence": False,
            "resource_availability": False,
            "management_integrity": False
        }
    }

@router.post("/{client_id}/acceptance")
def update_client_acceptance(
    client_id: int,
    data: dict, # { status: 'approved', checklist: {...} }
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # In a real implementation, we would save this to the DB
    # For MVP, we'll just return success
    return {"message": "Acceptance updated", "data": data}
