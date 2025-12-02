from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.api.database import get_db
from src.api import models
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/firm/certificates",
    tags=["certificates"]
)

@router.get("/", response_model=List[dict])
def list_certificates(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    certs = db.query(models.DigitalCertificate).filter(
        models.DigitalCertificate.firm_id == current_user.firm_id
    ).all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "filename": c.filename,
            "uploaded_at": c.uploaded_at
        }
        for c in certs
    ]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_certificate(
    name: str = Form(...),
    password: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(('.pfx', '.p12')):
        raise HTTPException(status_code=400, detail="Only .pfx or .p12 files are allowed")

    content = await file.read()

    # In a real app, encrypt the password here before saving
    # For MVP, we store it as is (User is aware this is a repository)
    password_enc = password

    cert = models.DigitalCertificate(
        firm_id=current_user.firm_id,
        name=name,
        filename=file.filename,
        file_content=content,
        password_enc=password_enc
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    return {"id": cert.id, "message": "Certificate uploaded successfully"}
