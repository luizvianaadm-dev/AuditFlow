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

@router.post("/{engagement_id}/letterhead", status_code=status.HTTP_201_CREATED)
def upload_letterhead(
    engagement_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Uploads a letterhead image (PNG/JPG) for the engagement reports.
    """
    # 1. Verify Engagement permissions
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # 2. Validate File Type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image (PNG, JPG)")

    # 3. Save File (Locally for now, S3/Cloudinary in Production)
    import os
    import shutil
    
    # Ensure directory exists
    UPLOAD_DIR = "static/letterheads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    filename = f"engagement_{engagement.id}_{int(datetime.now().timestamp())}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 4. Update Database
    engagement.client_letterhead_url = f"/static/letterheads/{filename}"
    db.commit()

    return {"message": "Letterhead uploaded successfully", "url": engagement.client_letterhead_url}

@router.post("/{engagement_id}/team", status_code=status.HTTP_200_OK)
def assign_team_members(
    engagement_id: int,
    members: List[int], # List of User IDs
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Assigns users to the engagement team.
    """
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # Clear existing team (Simple replacement logic for MVP)
    db.query(models.EngagementTeam).filter(models.EngagementTeam.engagement_id == engagement_id).delete()
    
    new_team = []
    for user_id in members:
        # Verify user belongs to firm
        user = db.query(models.User).filter(models.User.id == user_id, models.User.firm_id == current_user.firm_id).first()
        if user:
            team_member = models.EngagementTeam(
                engagement_id=engagement.id,
                user_id=user.id,
                role_in_engagement="Auditor" # Default role
            )
            new_team.append(team_member)
    
    db.add_all(new_team)
    db.commit()
    return {"message": "Team assigned successfully", "count": len(new_team)}
