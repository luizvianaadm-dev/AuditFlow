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

@router.get("/risk-factors")
def get_risk_factors():
    return materiality_engine.RISK_FACTORS

class MaterialityCalculationRequest(schemas.BaseModel):
    risks_present: List[str] = []

@router.post("/{engagement_id}/materiality/calculate")
def calculate_materiality_suggestion(
    engagement_id: int,
    request: MaterialityCalculationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Get Financial Data (Reuse logic)
    # ... (Same aggregation logic)
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

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
        if type_ == "Revenue": financial_data["gross_revenue"] = float(amount)
        elif type_ == "Asset": financial_data["total_assets"] = float(amount)
        elif type_ == "Equity": financial_data["equity"] = float(amount)
        if type_ == "Expense": financial_data["total_expenses"] = float(amount)

    rev = financial_data.get("gross_revenue", 0)
    exp = financial_data.get("total_expenses", 0)
    financial_data["net_profit"] = rev - exp

    # 2. Get Suggestion with Risks
    entity_type = "Empresarial"
    client_name = engagement.client.name.lower()
    if "condomini" in client_name or "assoc" in client_name:
        entity_type = "Condominio"

    suggestion = materiality_engine.suggest_benchmark(entity_type, financial_data, request.risks_present)
    
    # 3. Calculate Values based on Suggestion
    base = suggestion.get("base_value", 0)
    pct = suggestion.get("recommended_pct", 0)
    risk_score = suggestion.get("risk_score", 0)
    
    pm = materiality_engine.calculate_pm(base, pct)
    te = materiality_engine.calculate_te(pm, risk_score)
    ctt = materiality_engine.calculate_ctt(pm)
    
    # Apply Rounding (Adjusted Materiality)
    pm = materiality_engine.calculate_adjusted_materiality(pm)
    te = materiality_engine.calculate_adjusted_materiality(te)
    ctt = materiality_engine.calculate_adjusted_materiality(ctt)

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


# --- RISK MATRIX (SCOPING) ---

@router.get("/{engagement_id}/risk-matrix")
def get_risk_matrix(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Fetch Materiality
    materiality_record = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement_id,
        models.AnalysisResult.test_type == "materiality"
    ).order_by(models.AnalysisResult.created_at.desc()).first()

    if not materiality_record:
        # Default empty if no materiality
        return {"error": "Materiality not defined", "scoping": []}
    
    mat_data = materiality_record.result
    pm = mat_data.get("global_materiality", 0)
    te = mat_data.get("performance_materiality", 0)
    ctt = (pm * 0.05) # fallback if not saved

    # 2. Fetch Aggregated Data
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
        models.Transaction.engagement_id == engagement_id
    ).group_by(
        models.StandardAccount.code,
        models.StandardAccount.name,
        models.StandardAccount.type
    ).all()

    # 3. Fetch Saved Scoping (if any) to preserve overrides
    saved_scoping = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement_id,
        models.AnalysisResult.test_type == "risk_matrix"
    ).order_by(models.AnalysisResult.created_at.desc()).first()

    saved_map = {}
    if saved_scoping and saved_scoping.result:
        for item in saved_scoping.result.get("scoping", []):
             saved_map[item["account_code"]] = item

    scoping = []
    for code, name, type_, amount in results:
        val = float(amount)
        abs_val = abs(val)

        # Skip zero balances?
        if abs_val == 0: continue

        # Auto-Classification
        classification = "Non-Material"
        risk = "Low"
        strategy = "Analytical"
        
        if abs_val > pm:
            classification = "Key Item" # Critical
            risk = "High"
            strategy = "Substantive"
        elif abs_val > te:
            classification = "Significant"
            risk = "Medium"
            strategy = "Substantive"
        elif abs_val > ctt:
            classification = "Relevant"
            risk = "Low"
            strategy = "Analytical"
        else:
            classification = "Trivial"
            risk = "Low"
            strategy = "None"
        
        # Override if exists
        if code in saved_map:
            saved = saved_map[code]
            # Preserve user choices
            risk = saved.get("risk", risk)
            strategy = saved.get("strategy", strategy)
            # Classification is usually calc-based, but could be overridden? Keep calc for now.

        scoping.append({
            "account_code": code,
            "account_name": name,
            "account_type": type_,
            "balance": val,
            "abs_balance": abs_val,
            "pct_materiality": (abs_val / pm) if pm else 0,
            "classification": classification,
            "risk": risk,
            "strategy": strategy
        })
    
    # Sort by value desc
    scoping.sort(key=lambda x: x["abs_balance"], reverse=True)

    return {
        "materiality": { "pm": pm, "te": te, "ctt": ctt },
        "scoping": scoping
    }

@router.post("/{engagement_id}/risk-matrix")
def save_risk_matrix(
    engagement_id: int,
    data: Dict[str, Any], # { scoping: [...] }
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
        test_type="risk_matrix",
        result=data,
        executed_by_user_id=current_user.id
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return db_result



