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

        # --- 3.1 Initialize Default Departments ---
        default_depts = [
            {"name": "Administrativo", "is_overhead": True},
            {"name": "Financeiro", "is_overhead": True},
            {"name": "Recursos Humanos", "is_overhead": True},
            {"name": "Comercial", "is_overhead": True},
            {"name": "Jurídico", "is_overhead": True},
            {"name": "Auditoria", "is_overhead": False},
        ]
        
        dept_map = {}
        for dept in default_depts:
            new_dept = models.Department(name=dept["name"], is_overhead=dept["is_overhead"], firm_id=new_firm.id)
            db.add(new_dept)
            db.flush()
            dept_map[dept["name"]] = new_dept.id

        # --- 3.2 Initialize Default Job Roles ---
        default_roles = [
            {"name": "Sócio", "level": 1, "hourly_rate": 500.0},
            {"name": "Diretor", "level": 2, "hourly_rate": 400.0},
            {"name": "Gerente Sênior", "level": 3, "hourly_rate": 350.0},
            {"name": "Gerente", "level": 4, "hourly_rate": 300.0},
            {"name": "Supervisor A", "level": 5, "hourly_rate": 250.0},
            {"name": "Supervisor B", "level": 6, "hourly_rate": 220.0},
            {"name": "Sênior A", "level": 7, "hourly_rate": 180.0},
            {"name": "Sênior B", "level": 8, "hourly_rate": 160.0},
            {"name": "Sênior C", "level": 9, "hourly_rate": 140.0},
            {"name": "Assistente A", "level": 10, "hourly_rate": 100.0},
            {"name": "Assistente B", "level": 11, "hourly_rate": 80.0},
            {"name": "Trainee", "level": 12, "hourly_rate": 50.0},
            {"name": "Estagiário", "level": 13, "hourly_rate": 30.0},
        ]

        role_map = {}
        for role in default_roles:
            new_role = models.JobRole(
                name=role["name"], 
                level=role["level"], 
                hourly_rate=role["hourly_rate"], 
                firm_id=new_firm.id
            )
            db.add(new_role)
            db.flush()
            role_map[role["name"]] = new_role.id

        # 4. Create Admin User (Sócio)
        hashed_pwd = security.get_password_hash(firm_data.password)
        role = "admin" # System role

        new_user = models.User(
            email=firm_data.email,
            hashed_password=hashed_pwd,
            role=role,
            firm_id=new_firm.id,
            terms_accepted=firm_data.termsAccepted,
            terms_accepted_at=datetime.utcnow() if firm_data.termsAccepted else None,
            
            # Map Profile Data
            cpf=firm_data.cpf,
            phone=firm_data.phone,
            
            # Assign Initial Hierarchy
            department_id=dept_map.get("Administrativo"),
            job_role_id=role_map.get("Sócio")
        )
        db.add(new_user)
        
        db.commit()
        db.refresh(new_firm)
        return new_firm

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
