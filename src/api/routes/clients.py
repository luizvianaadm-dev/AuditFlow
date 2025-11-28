from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
from datetime import datetime

from src.api.database import get_db
from src.api import models, schemas

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)

@router.post("/", response_model=schemas.ClientRead)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    # Check if firm exists
    firm = db.query(models.AuditFirm).filter(models.AuditFirm.id == client.firm_id).first()
    if not firm:
        raise HTTPException(status_code=404, detail="Audit Firm not found")

    db_client = models.Client(name=client.name, firm_id=client.firm_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/", response_model=List[schemas.ClientRead])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clients = db.query(models.Client).offset(skip).limit(limit).all()
    return clients

@router.post("/{client_id}/upload-ledger", status_code=status.HTTP_201_CREATED)
async def upload_ledger(client_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Uploads a general ledger CSV and creates transactions for the client.
    Creates a new Engagement automatically named 'Imported Ledger {Timestamp}'.
    """
    # 1. Verify Client
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 2. Parse CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        content = await file.read()
        # Assume CSV has columns: Date, Description, Vendor, Amount
        # Or at least Vendor, Amount.
        df = pd.read_csv(io.BytesIO(content))

        required_cols = {'vendor', 'amount'}
        # Normalize columns to lowercase for checking
        df.columns = [c.lower() for c in df.columns]

        if not required_cols.issubset(set(df.columns)):
             raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_cols}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")

    # 3. Create Engagement
    current_year = datetime.now().year
    engagement_name = f"Imported Ledger {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    new_engagement = models.Engagement(
        name=engagement_name,
        year=current_year,
        client_id=client.id
    )
    db.add(new_engagement)
    db.commit()
    db.refresh(new_engagement)

    # 4. Create Transactions
    transactions = []
    for _, row in df.iterrows():
        # Handle date if present
        tx_date = None
        if 'date' in df.columns and pd.notna(row['date']):
            try:
                tx_date = pd.to_datetime(row['date']).to_pydatetime()
            except:
                pass # Keep None if parse fails

        tx = models.Transaction(
            engagement_id=new_engagement.id,
            vendor=str(row['vendor']),
            amount=float(row['amount']),
            description=str(row.get('description', '')),
            date=tx_date
        )
        transactions.append(tx)

    db.add_all(transactions)
    db.commit()

    return {"message": f"Successfully imported {len(transactions)} transactions to engagement '{engagement_name}'"}
