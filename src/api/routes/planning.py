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

from src.api.services.materiality import materiality_engine

@router.post("/{engagement_id}/materiality/calculate")
def calculate_materiality_suggestion(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Get Financial Data (Reuse logic or call internal function)
    # For MVP, we reproduce the aggregation logic briefly or refactor.
    # We'll use the aggregated values.
    
    # Verify Engagement (and get type)
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # Aggregate Transactions
    results = db.query(
        models.StandardAccount.type,
        func.sum(models.Transaction.amount).label("total_amount")
    ).join(
        models.AccountMapping,
        models.AccountMapping.standard_account_id == models.StandardAccount.id
    ).join(
        models.Transaction,
        models.Transaction.account_name == models.AccountMapping.client_description
    ).filter(
        models.Transaction.engagement_id == engagement_id
    ).group_by(
        models.StandardAccount.type
    ).all()

    financial_data = {}
    for type_, amount in results:
        # StandardAccount types mapping to Engine keys
        if type_ == "Revenue": financial_data["gross_revenue"] = float(amount)
        elif type_ == "Asset": financial_data["total_assets"] = float(amount)
        elif type_ == "Equity": financial_data["equity"] = float(amount)
        # Net Profit needs calculation (Revenue - Expenses), approximate for MVP
        # Expenses
        if type_ == "Expense": financial_data["total_expenses"] = float(amount)

    # Calculate Net Profit (Roughly)
    rev = financial_data.get("gross_revenue", 0)
    exp = financial_data.get("total_expenses", 0)
    financial_data["net_profit"] = rev - exp

    # 2. Get Suggestion
    # Determine entity type (Client.entity_type or similar). 
    # Provided Schema doesn't specify, we default to Empresarial unless Client name suggests Condominio
    # Or add column later. For now, check client name?
    entity_type = "Empresarial"
    client_name = engagement.client.name.lower()
    if "condomini" in client_name or "assoc" in client_name:
        entity_type = "Condominio"

    suggestion = materiality_engine.suggest_benchmark(entity_type, financial_data)
    
    # 3. Calculate Values based on Suggestion
    base = suggestion.get("base_value", 0)
    pct = suggestion.get("recommended_pct", 0)
    
    pm = materiality_engine.calculate_pm(base, pct)
    te = materiality_engine.calculate_te(pm, "normal") # Default to Normal Risk
    ctt = materiality_engine.calculate_ctt(pm)

    return {
        "entity_type": entity_type,
        "financial_data": financial_data,
        "suggestion": suggestion,
        "calculated_values": {
            "pm": pm,
            "te": te,
            "ctt": ctt
        }
    }

