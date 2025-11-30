from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import pandas as pd
import io

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/engagements",
    tags=["payroll"]
)

@router.post("/{engagement_id}/payroll/upload", status_code=status.HTTP_201_CREATED)
def upload_payroll_summary(
    engagement_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Uploads a Payroll Summary CSV (Folha de Pagamento Sintética).
    Expected columns: code, name, gross_salary, inss, fgts, net_pay
    This data is stored temporarily in AnalysisResult or a dedicated table.
    For MVP, we will process and store the summary in AnalysisResult directly as 'payroll_data'.
    """
    # Verify Engagement
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        content = file.file.read()
        df = pd.read_csv(io.BytesIO(content))
        df.columns = [c.lower().strip() for c in df.columns]

        required = {'gross_salary', 'inss', 'fgts'}
        if not required.issubset(set(df.columns)):
             raise HTTPException(status_code=400, detail=f"CSV must contain: {required}")

        # Calculate totals
        summary = {
            "total_gross": float(df['gross_salary'].sum()),
            "total_inss": float(df['inss'].sum()),
            "total_fgts": float(df['fgts'].sum()),
            "employee_count": len(df),
            "details": df.to_dict(orient='records') # Be careful with size here in production
        }

        # Save as a raw payroll upload result
        db_result = models.AnalysisResult(
            engagement_id=engagement.id,
            test_type="payroll_upload",
            result=summary,
            executed_by_user_id=current_user.id
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)

        return db_result

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.post("/{engagement_id}/payroll/reconcile", response_model=schemas.AnalysisResultRead)
def reconcile_payroll(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Fetch latest payroll upload
    payroll_upload = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement_id,
        models.AnalysisResult.test_type == "payroll_upload"
    ).order_by(models.AnalysisResult.executed_at.desc()).first()

    if not payroll_upload:
        raise HTTPException(status_code=400, detail="No payroll data found. Upload payroll summary first.")

    payroll_data = payroll_upload.result

    # 2. Fetch Accounting Data (General Ledger)
    # We look for transactions mapped to "Despesas com Pessoal" or similar standard accounts.
    # We assume standard accounts for Expense (Type='Expense') roughly cover payroll if filtered.
    # For MVP, we sum ALL 'Expense' transactions that contain 'SALARIO', 'FOLHA', 'INSS', 'FGTS' in description if mapping isn't perfect,
    # OR better, rely on the StandardAccount structure seeded.
    # In seed_accounts.py, we have "2.1.02" (Obrigações Trabalhistas) and "201" (Pessoal e Encargos - Condo).
    # Let's try to find mapped transactions first.

    # Find standard accounts related to Payroll
    payroll_keywords = ['pessoal', 'salario', 'ordenado', 'inss', 'fgts', 'previdencia', 'trabalhista']

    # Get all standard accounts IDs that match keywords
    std_accounts = db.query(models.StandardAccount).filter(
        models.StandardAccount.name.ilike('%pessoal%') |
        models.StandardAccount.name.ilike('%trabalhista%') |
        models.StandardAccount.name.ilike('%salario%')
    ).all()
    std_ids = [sa.id for sa in std_accounts]

    # Sum transactions mapped to these standard accounts
    accounting_sum = db.query(func.sum(models.Transaction.amount)).join(
        models.AccountMapping, models.AccountMapping.client_description == models.Transaction.account_name
    ).filter(
        models.Transaction.engagement_id == engagement_id,
        models.AccountMapping.standard_account_id.in_(std_ids)
    ).scalar() or 0.0

    # If mapping is weak, fallback to description search (Simulating robust logic)
    if accounting_sum == 0:
        accounting_sum = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.engagement_id == engagement_id,
            models.Transaction.description.ilike('%folha%') |
            models.Transaction.description.ilike('%salario%') |
            models.Transaction.description.ilike('%inss%')
        ).scalar() or 0.0

    # 3. Compare
    # Payroll System Total (Gross + Encargos usually, or just Gross depending on what 'Total' means in context)
    # Let's compare Gross vs Accounting Expense roughly

    comparison = {
        "payroll_system_gross": payroll_data['total_gross'],
        "payroll_system_inss": payroll_data['total_inss'],
        "payroll_system_fgts": payroll_data['total_fgts'],
        "accounting_total": accounting_sum,
        "difference": accounting_sum - (payroll_data['total_gross'] + payroll_data['total_inss'] + payroll_data['total_fgts']), # Simplistic formula
        "status": "divergent" if abs(accounting_sum - (payroll_data['total_gross'])) > 100 else "reconciled"
    }

    # Save Reconciliation Result
    db_result = models.AnalysisResult(
        engagement_id=engagement_id,
        test_type="payroll_reconciliation",
        result=comparison,
        executed_by_user_id=current_user.id
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return db_result
