from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.api.database import get_db
from src.api import models, schemas, security
from src.api.deps import get_current_user
from src.api.utils.email import send_email

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
async def invite_user(
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

    new_user = models.User(
        email=invite.email,
        hashed_password=hashed_password,
        role=invite.role,
        position=invite.position,
        firm_id=current_user.firm_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send invite email
    try:
        await send_email(
            recipients=[new_user.email],
            subject="Convite para AuditFlow",
            body=f"""
            Olá,<br><br>
            Você foi convidado para participar da firma no AuditFlow.<br>
            Sua senha temporária é: {invite.password}<br>
            Por favor, acesse o sistema e altere sua senha.<br><br>
            AuditFlow Team
            """
        )
    except Exception as e:
        print(f"Failed to send invite email: {e}")

    return new_user
