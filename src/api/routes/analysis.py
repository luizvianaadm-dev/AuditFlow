from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user
from src.scripts.benford_analysis import calculate_benford
from src.scripts.duplicate_analysis import find_duplicates

router = APIRouter(
    prefix="/engagements",
    tags=["analysis"]
)

@router.post("/{engagement_id}/run-benford", response_model=schemas.AnalysisResultRead)
def run_benford_analysis(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Engagement belongs to user's firm
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # Get values
    values = [t.amount for t in engagement.transactions if t.amount is not None]
    if not values:
        raise HTTPException(status_code=400, detail="No transactions found for this engagement")

    # Run Analysis
    result = calculate_benford(values)

    # Save Result
    db_result = models.AnalysisResult(
        engagement_id=engagement.id,
        test_type="benford",
        result=result,
        executed_by_user_id=current_user.id
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return db_result

@router.post("/{engagement_id}/run-duplicates", response_model=schemas.AnalysisResultRead)
def run_duplicate_analysis(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Engagement belongs to user's firm
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # Convert transactions to dicts for the script
    transactions_dicts = [
        {"id": t.id, "vendor": t.vendor, "amount": t.amount, "date": str(t.date) if t.date else None}
        for t in engagement.transactions
    ]

    if not transactions_dicts:
        raise HTTPException(status_code=400, detail="No transactions found for this engagement")

    # Run Analysis
    result = find_duplicates(transactions_dicts)

    # Save Result (Wrap list in dict for JSON storage if needed, or sqlalchemy handles list of dicts as JSON array usually)
    # SQLAlchemy JSON type handles primitives, lists, and dicts.

    db_result = models.AnalysisResult(
        engagement_id=engagement.id,
        test_type="duplicates",
        result={"duplicates": result}, # Wrap in object for clarity
        executed_by_user_id=current_user.id
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return db_result

@router.get("/{engagement_id}/results", response_model=List[schemas.AnalysisResultRead])
def read_analysis_results(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Engagement permissions
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # Sort by execution date desc
    return db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement.id
    ).order_by(models.AnalysisResult.executed_at.desc()).all()
