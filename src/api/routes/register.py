from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from src.api.database import get_db
from src.api import models, schemas, security

router = APIRouter(tags=["registration"])

@router.post("/register", response_model=schemas.AuditFirmRead)
def register_firm(firm_data: schemas.FirmRegister, db: Session = Depends(get_db)):
    # 1. Check if firm (CNPJ) already exists
    existing_firm = db.query(models.AuditFirm).filter(models.AuditFirm.cnpj == firm_data.cnpj).first()
    if existing_firm:
        raise HTTPException(status_code=400, detail="Firm with this CNPJ already registered")

    # 2. Check if user (Email) already exists
    existing_user = db.query(models.User).filter(models.User.email == firm_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        # 3. Create Firm
        new_firm = models.AuditFirm(
            name=firm_data.companyName,
            cnpj=firm_data.cnpj,
            crc_registration=firm_data.crc_registration,
            cnai=firm_data.cnai,
            cnai_expiration_date=firm_data.cnai_expiration_date,
            cvm_registration=firm_data.cvm_registration
        )
        db.add(new_firm)
        db.flush() # Flush to get ID

        # 4. Create Admin User
        hashed_pwd = security.get_password_hash(firm_data.password)
        role = "admin" # Default for firm creator
        
        # Vorcon Special Access
        if firm_data.email.endswith("@vorcon.com.br"):
            # Auto-assign Enterprise Plan mock? 
            # For now, just ensuring they are admins is enough as per current "role" column.
            pass

        new_user = models.User(
            email=firm_data.email,
            hashed_password=hashed_pwd,
            role=role,
            firm_id=new_firm.id,
            terms_accepted=firm_data.termsAccepted,
            terms_accepted_at=datetime.utcnow() if firm_data.termsAccepted else None
        )
        db.add(new_user)

        db.commit()
        db.refresh(new_firm)
        return new_firm

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
