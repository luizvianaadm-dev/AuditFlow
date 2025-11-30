from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/engagements",
    tags=["planning"]
)

@router.get("/{engagement_id}/financial-summary")
def get_financial_summary(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Engagement
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # 1. Fetch all transactions with their mapped Standard Account
    # We join Transaction -> AccountMapping (on name matching client_description) -> StandardAccount
    # Note: This is an exact match on string.
    # In a real scenario, we might link transaction directly to mapping ID during upload or processing.
    # For now, we do a join based on the string.

    results = db.query(
        models.StandardAccount.code,
        models.StandardAccount.name,
        models.StandardAccount.type,
        func.sum(models.Transaction.amount).label("total_amount")
    ).join(
        models.AccountMapping,
        models.AccountMapping.standard_account_id == models.StandardAccount.id
    ).join(
        models.Transaction,
        models.Transaction.account_name == models.AccountMapping.client_description
    ).filter(
        models.Transaction.engagement_id == engagement_id,
        models.AccountMapping.firm_id == current_user.firm_id
    ).group_by(
        models.StandardAccount.code,
        models.StandardAccount.name,
        models.StandardAccount.type
    ).all()

    # Calculate Totals for Key Groups (Assets, Liabilities, Revenue)
    summary = {
        "assets": 0.0,
        "liabilities": 0.0,
        "equity": 0.0,
        "revenue": 0.0,
        "expenses": 0.0,
        "details": []
    }

    for code, name, type_, amount in results:
        # Simple classification based on Type or Code prefix
        if type_ == "Asset": summary["assets"] += amount
        elif type_ == "Liability": summary["liabilities"] += amount
        elif type_ == "Equity": summary["equity"] += amount
        elif type_ == "Revenue": summary["revenue"] += amount
        elif type_ == "Expense": summary["expenses"] += amount

        summary["details"].append({
            "code": code,
            "name": name,
            "type": type_,
            "amount": amount
        })

    return summary

@router.post("/{engagement_id}/materiality", response_model=schemas.AnalysisResultRead)
def save_materiality_calculation(
    engagement_id: int,
    calculation_data: Dict[str, Any], # { benchmark: 'Revenue', percentage: 5, value: 10000 }
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Engagement
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # Save as AnalysisResult
    db_result = models.AnalysisResult(
        engagement_id=engagement.id,
        test_type="materiality",
        result=calculation_data,
        executed_by_user_id=current_user.id
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return db_result
