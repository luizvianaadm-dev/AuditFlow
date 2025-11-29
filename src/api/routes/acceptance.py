from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/clients",
    tags=["acceptance"]
)

@router.get("/{client_id}/acceptance", response_model=Optional[schemas.AcceptanceFormRead])
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

    acceptance = db.query(models.AcceptanceForm).filter(models.AcceptanceForm.client_id == client_id).first()
    return acceptance

@router.post("/{client_id}/acceptance", response_model=schemas.AcceptanceFormRead)
def create_or_update_acceptance(
    client_id: int,
    form_data: schemas.AcceptanceFormCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    client = db.query(models.Client).filter(
        models.Client.id == client_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Determine status
    # If all checks are true, approved. Else rejected (or pending if logic differs)
    status_result = "approved" if (
        form_data.independence_check and
        form_data.integrity_check and
        form_data.competence_check and
        not form_data.conflict_check # Conflict should be False
    ) else "rejected"

    existing = db.query(models.AcceptanceForm).filter(models.AcceptanceForm.client_id == client_id).first()

    if existing:
        existing.independence_check = form_data.independence_check
        existing.integrity_check = form_data.integrity_check
        existing.competence_check = form_data.competence_check
        existing.conflict_check = form_data.conflict_check
        existing.comments = form_data.comments
        existing.status = status_result
        existing.created_by_user_id = current_user.id
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_form = models.AcceptanceForm(
            client_id=client_id,
            created_by_user_id=current_user.id,
            independence_check=form_data.independence_check,
            integrity_check=form_data.integrity_check,
            competence_check=form_data.competence_check,
            conflict_check=form_data.conflict_check,
            comments=form_data.comments,
            status=status_result
        )
        db.add(new_form)
        db.commit()
        db.refresh(new_form)
        return new_form
