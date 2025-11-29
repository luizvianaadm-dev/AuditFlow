from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/clients",
    tags=["engagements"]
)

@router.get("/{client_id}/engagements", response_model=List[schemas.EngagementRead])
def read_engagements(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Client belongs to user's firm
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client.engagements

@router.post("/{client_id}/engagements", response_model=schemas.EngagementRead)
def create_engagement(
    client_id: int,
    engagement: schemas.EngagementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Client belongs to user's firm
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db_engagement = models.Engagement(
        name=engagement.name,
        year=engagement.year,
        client_id=client.id
    )
    db.add(db_engagement)
    db.commit()
    db.refresh(db_engagement)
    return db_engagement
