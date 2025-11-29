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
    prefix="/engagements", # Changed prefix to /engagements for clarity
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

        required_cols = {'vendor', 'amount'}
        df.columns = [c.lower() for c in df.columns]

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

        tx = models.Transaction(
            engagement_id=engagement.id,
            vendor=str(row['vendor']),
            amount=float(row['amount']),
            description=str(row.get('description', '')),
            date=tx_date
        )
        transactions.append(tx)

    db.add_all(transactions)
    db.commit()

    return {"message": f"Successfully imported {len(transactions)} transactions."}
