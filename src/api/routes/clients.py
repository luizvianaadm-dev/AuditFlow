from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)

@router.post("/", response_model=schemas.ClientRead)
def create_client(
    client: schemas.ClientBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing = db.query(models.Client).filter(
        models.Client.firm_id == current_user.firm_id,
        models.Client.name == client.name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Client already exists for this firm")

    db_client = models.Client(name=client.name, firm_id=current_user.firm_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/", response_model=List[schemas.ClientRead])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    clients = db.query(models.Client).filter(
        models.Client.firm_id == current_user.firm_id
    ).offset(skip).limit(limit).all()
    return clients

# --- Sub-resource: Engagements ---

@router.get("/{client_id}/engagements", response_model=List[schemas.EngagementRead])
def read_client_engagements(
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

    return client.engagements

@router.post("/{client_id}/engagements", response_model=schemas.EngagementRead)
def create_client_engagement(
    client_id: int,
    engagement: schemas.EngagementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db_engagement = models.Engagement(
        name=engagement.name,
        year=engagement.year,
        service_type=engagement.service_type,
        client_id=client.id
    )
    db.add(db_engagement)
    db.commit()
    db.refresh(db_engagement)
    return db_engagement
