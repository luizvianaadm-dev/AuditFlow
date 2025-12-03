from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import pandas as pd
import io

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/engagements",
    tags=["engagements"]
)

@router.get("/{engagement_id}/transactions", response_model=List[schemas.TransactionRead])
def read_engagement_transactions(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Engagement belongs to user's firm via Client
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    return engagement.transactions

@router.post("/{engagement_id}/upload", status_code=status.HTTP_201_CREATED)
def upload_transactions_to_engagement(
    engagement_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Uploads a CSV to an existing engagement.
    Supported columns: vendor, amount, date, description, account_code, account_name
    """
    # 1. Verify Engagement permissions
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # 2. Parse CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        content = file.file.read()
        df = pd.read_csv(io.BytesIO(content))

        # Normalize columns
        df.columns = [c.lower().strip() for c in df.columns]

        # Basic Validation
        required_cols = {'vendor', 'amount'}
        if not required_cols.issubset(set(df.columns)):
             raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_cols}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")

    # 3. Create Transactions
    transactions = []
    for _, row in df.iterrows():
        tx_date = None
        if 'date' in df.columns and pd.notna(row['date']):
            try:
                tx_date = pd.to_datetime(row['date']).to_pydatetime()
            except:
                pass

        # Extract account info if present (supports aliases)
        account_code = str(row.get('account_code') or row.get('conta') or row.get('code') or '')
        if account_code == 'nan': account_code = None

        account_name = str(row.get('account_name') or row.get('description') or row.get('descricao') or '')
        if account_name == 'nan': account_name = None

        tx = models.Transaction(
            engagement_id=engagement.id,
            vendor=str(row['vendor']),
            amount=float(row['amount']),
            description=str(row.get('description', '')),
            date=tx_date,
            account_code=account_code,
            account_name=account_name
        )
        transactions.append(tx)

    db.add_all(transactions)
    db.commit()

    return {"message": f"Successfully imported {len(transactions)} transactions."}

@router.get("/{engagement_id}/trial-balance", response_model=List[dict])
def read_trial_balance(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    return [
        {
            "id": tb.id,
            "account_code": tb.account_code,
            "account_description": tb.account_description,
            "initial_balance": tb.initial_balance,
            "debits": tb.debits,
            "credits": tb.credits,
            "final_balance": tb.final_balance
        }
        for tb in engagement.trial_balance_entries
    ]

@router.post("/{engagement_id}/upload-trial-balance-full", status_code=status.HTTP_201_CREATED)
async def upload_trial_balance_full(
    engagement_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Uploads a full 4-column Trial Balance (Original Client Plan).
    Expected columns (flexible): code, description, initial, debits, credits, final
    """
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    try:
        content = await file.read()

        df = None
        if file.filename.lower().endswith('.csv'):
             df = pd.read_csv(io.BytesIO(content), sep=None, engine='python') # Auto-detect sep
        elif file.filename.lower().endswith(('.xls', '.xlsx')):
             df = pd.read_excel(io.BytesIO(content))
        else:
             raise HTTPException(status_code=400, detail="Invalid file type")

        # Standardize columns
        df.columns = [str(c).lower().strip() for c in df.columns]

        # Mapping helpers
        col_map = {
            'account_code': ['cod', 'codigo', 'conta', 'account_code'],
            'account_description': ['descricao', 'desc', 'nome', 'description', 'historico'],
            'initial_balance': ['saldo_anterior', 'saldo_inicial', 'initial', 'anterior'],
            'debits': ['debito', 'debitos', 'debit', 'db'],
            'credits': ['credito', 'creditos', 'credit', 'cr'],
            'final_balance': ['saldo_atual', 'saldo_final', 'final', 'balance', 'saldo']
        }

        final_cols = {}
        for target, keywords in col_map.items():
            for col in df.columns:
                if any(k in col for k in keywords):
                    final_cols[target] = col
                    break

        if 'account_description' not in final_cols:
             raise HTTPException(status_code=400, detail="Could not find Account Description column")

        # Clear existing entries for this engagement (Full Replace)
        db.query(models.TrialBalanceEntry).filter(models.TrialBalanceEntry.engagement_id == engagement_id).delete()

        entries = []
        for _, row in df.iterrows():

            def clean_val(val):
                if pd.isna(val): return 0.0
                try:
                    s = str(val).strip()
                    if ',' in s and '.' in s: # 1.000,00
                        s = s.replace('.', '').replace(',', '.')
                    elif ',' in s: # 1000,00
                        s = s.replace(',', '.')
                    return float(s)
                except:
                    return 0.0

            entry = models.TrialBalanceEntry(
                engagement_id=engagement_id,
                account_code=str(row[final_cols['account_code']]) if 'account_code' in final_cols else None,
                account_description=str(row[final_cols['account_description']]),
                initial_balance=clean_val(row.get(final_cols.get('initial_balance'))),
                debits=clean_val(row.get(final_cols.get('debits'))),
                credits=clean_val(row.get(final_cols.get('credits'))),
                final_balance=clean_val(row.get(final_cols.get('final_balance')))
            )
            entries.append(entry)

        db.add_all(entries)
        db.commit()
        return {"message": f"Uploaded {len(entries)} trial balance rows."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")
