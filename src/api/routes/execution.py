from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
import datetime

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/engagements",
    tags=["execution"]
)

# --- WORKPAPERS (Schemaless via AnalysisResult) ---

@router.get("/{engagement_id}/workpapers")
def get_workpapers(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Fetch all results of type 'workpaper'
    results = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement_id,
        models.AnalysisResult.test_type.like("workpaper_%")
    ).all()

    return results

@router.get("/{engagement_id}/workpapers/{account_code}")
def get_or_create_workpaper(
    engagement_id: int,
    account_code: str,
    account_name: Optional[str] = None, # Passed for convenience init
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if exists
    test_type = f"workpaper_{account_code}"
    wp = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement_id,
        models.AnalysisResult.test_type == test_type
    ).first()

    if wp:
        return wp

    # Create New (Initialize with standard procedures based on type?)
    # For now, generic procedures.
    initial_result = {
        "account_code": account_code,
        "account_name": account_name or "Unknown",
        "status": "In Progress",
        "procedures": [
            {"id": "obj", "label": "Definir Objetivos de Auditoria", "checked": False},
            {"id": "math", "label": "Conferência de Cálculos Matemáticos", "checked": False},
            {"id": "docs", "label": "Inspeção Documental (Voucher)", "checked": False},
            {"id": "cutoff", "label": "Teste de Cut-off (Competência)", "checked": False},
        ],
        "findings": [],
        "conclusion": ""
    }

    new_wp = models.AnalysisResult(
        engagement_id=engagement_id,
        test_type=test_type,
        result=initial_result,
        executed_by_user_id=current_user.id
    )
    db.add(new_wp)
    db.commit()
    db.refresh(new_wp)
    return new_wp

@router.post("/{engagement_id}/workpapers/{account_code}")
def update_workpaper(
    engagement_id: int,
    account_code: str,
    data: Dict[str, Any], # Full result JSON
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    test_type = f"workpaper_{account_code}"
    wp = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement_id,
        models.AnalysisResult.test_type == test_type
    ).first()

    if not wp:
        raise HTTPException(status_code=404, detail="Workpaper not found")
    
    wp.result = data
    wp.updated_at = datetime.datetime.utcnow()
    # wp.executed_by_user_id = current_user.id # Optional update
    
    db.commit()
    db.refresh(wp)
    return wp
