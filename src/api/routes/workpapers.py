from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/workpapers",
    tags=["workpapers"]
)

# Reuse engagement dependency logic or keep simple check
def get_engagement(engagement_id: int, db: Session, user: models.User):
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == user.firm_id
    ).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return engagement

@router.post("/engagements/{engagement_id}/generate")
def generate_workpapers(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = get_engagement(engagement_id, db, current_user)

    # 1. Identify Template
    template = engagement.service_type # e.g. 'br_gaap'

    # 2. Fetch Standard Audit Areas/Procedures for this template
    areas = db.query(models.AuditArea).filter(models.AuditArea.template_type == template).all()

    if not areas:
        # Fallback to br_gaap if specific template empty
        areas = db.query(models.AuditArea).filter(models.AuditArea.template_type == 'br_gaap').all()

    count = 0
    for area in areas:
        for proc in area.procedures:
            # Check if WP already exists
            existing = db.query(models.WorkPaper).filter(
                models.WorkPaper.engagement_id == engagement.id,
                models.WorkPaper.procedure_id == proc.id
            ).first()

            if not existing:
                wp = models.WorkPaper(
                    engagement_id=engagement.id,
                    procedure_id=proc.id,
                    status='open'
                )
                db.add(wp)
                count += 1

    db.commit()
    return {"message": f"Generated {count} workpapers."}

@router.get("/engagements/{engagement_id}", response_model=Dict[str, Any])
def list_workpapers(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = get_engagement(engagement_id, db, current_user)

    # Group by Area
    # Join WorkPaper -> Procedure -> Area
    results = db.query(models.WorkPaper).join(models.AuditProcedure).join(models.AuditArea).filter(
        models.WorkPaper.engagement_id == engagement.id
    ).all()

    # Structure output: { "Area Name": [ {wp_details}, ... ] }
    grouped = {}
    for wp in results:
        area_name = wp.procedure.area.name
        if area_name not in grouped:
            grouped[area_name] = []

        grouped[area_name].append({
            "id": wp.id,
            "description": wp.procedure.description,
            "status": wp.status,
            "comments": wp.comments,
            "completed_at": wp.completed_at
        })

    return grouped

@router.post("/{workpaper_id}/update")
def update_workpaper(
    workpaper_id: int,
    data: Dict[str, Any], # { status, comments }
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Security: join through engagement...client...firm
    wp = db.query(models.WorkPaper).join(models.Engagement).join(models.Client).filter(
        models.WorkPaper.id == workpaper_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not wp:
        raise HTTPException(status_code=404, detail="Workpaper not found")

    if 'status' in data:
        wp.status = data['status']
        if wp.status == 'completed':
            wp.completed_at = datetime.utcnow()
            wp.assigned_to_user_id = current_user.id # completed by
    if 'comments' in data:
        wp.comments = data['comments']

    db.commit()
    return {"message": "Updated"}

# --- Mistatements ---

@router.post("/engagements/{engagement_id}/mistatements")
def add_mistatement(
    engagement_id: int,
    data: Dict[str, Any], # { description, amount, type }
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = get_engagement(engagement_id, db, current_user)

    mistatement = models.Mistatement(
        engagement_id=engagement.id,
        description=data.get('description'),
        amount_divergence=data.get('amount'),
        type=data.get('type', 'factual'),
        workpaper_id=data.get('workpaper_id')
    )
    db.add(mistatement)
    db.commit()
    return {"message": "Mistatement recorded"}

@router.get("/engagements/{engagement_id}/summary-of-mistatements")
def get_mistatement_summary(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = get_engagement(engagement_id, db, current_user)

    items = db.query(models.Mistatement).filter(models.Mistatement.engagement_id == engagement.id).all()

    total_adjusted = sum(i.amount_divergence for i in items if i.status == 'adjusted')
    total_unadjusted = sum(i.amount_divergence for i in items if i.status == 'open' or i.status == 'unadjusted')

    # Get Materiality if exists
    materiality_result = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement.id,
        models.AnalysisResult.test_type == "materiality"
    ).order_by(models.AnalysisResult.executed_at.desc()).first()

    materiality = materiality_result.result if materiality_result else {}

    return {
        "items": items,
        "total_adjusted": total_adjusted,
        "total_unadjusted": total_unadjusted,
        "materiality": materiality
    }
