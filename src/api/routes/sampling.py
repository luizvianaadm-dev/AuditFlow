from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import random

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/engagements",
    tags=["sampling"]
)

@router.post("/{engagement_id}/sampling/random", response_model=schemas.AnalysisResultRead)
def run_random_sampling(
    engagement_id: int,
    params: Dict[str, Any], # { sample_size: 20, seed: 42 }
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    transactions = engagement.transactions
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions to sample")

    sample_size = int(params.get('sample_size', 10))
    if sample_size > len(transactions):
        sample_size = len(transactions)

    # Random selection
    # Using python's random for MVP. In production, use numpy/pandas for large datasets.
    selected_txs = random.sample(transactions, sample_size)

    result_data = {
        "method": "random",
        "population_size": len(transactions),
        "sample_size": sample_size,
        "items": [
            {
                "id": t.id,
                "vendor": t.vendor,
                "amount": t.amount,
                "date": str(t.date) if t.date else None,
                "account": t.account_name
            } for t in selected_txs
        ]
    }

    db_result = models.AnalysisResult(
        engagement_id=engagement.id,
        test_type="sampling",
        result=result_data,
        executed_by_user_id=current_user.id
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return db_result

@router.post("/{engagement_id}/sampling/stratified", response_model=schemas.AnalysisResultRead)
def run_stratified_sampling(
    engagement_id: int,
    params: Dict[str, Any], # { threshold: 1000, sample_size_below: 10 }
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    transactions = engagement.transactions
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions to sample")

    threshold = float(params.get('threshold', 0))
    sample_size_below = int(params.get('sample_size_below', 10))

    # Stratification logic: Select ALL above threshold, Random below
    high_value = [t for t in transactions if (t.amount or 0) >= threshold]
    low_value = [t for t in transactions if (t.amount or 0) < threshold]

    if sample_size_below > len(low_value):
        sample_size_below = len(low_value)

    selected_low = random.sample(low_value, sample_size_below)

    final_sample = high_value + selected_low

    result_data = {
        "method": "stratified",
        "population_size": len(transactions),
        "threshold": threshold,
        "high_value_count": len(high_value),
        "low_value_sample_count": len(selected_low),
        "total_sample_size": len(final_sample),
        "items": [
            {
                "id": t.id,
                "vendor": t.vendor,
                "amount": t.amount,
                "date": str(t.date) if t.date else None,
                "reason": "High Value" if (t.amount or 0) >= threshold else "Random Selection"
            } for t in final_sample
        ]
    }

    db_result = models.AnalysisResult(
        engagement_id=engagement.id,
        test_type="sampling",
        result=result_data,
        executed_by_user_id=current_user.id
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return db_result
