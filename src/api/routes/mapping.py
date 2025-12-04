from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from src.api.services.ingestion import TrialBalanceIngestion
from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user

router = APIRouter(
    prefix="/mapping",
    tags=["mapping"]
)

@router.get("/standard-accounts", response_model=List[schemas.StandardAccountRead])
def list_standard_accounts(
    client_id: Optional[int] = Query(None),
    template_type: str = Query("br_gaap"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns standard accounts.
    If client_id is provided, returns accounts specific to that client OR global ones.
    However, usually we either want System Standard OR Client Custom.
    """
    query = db.query(models.StandardAccount)

    if client_id:
        # If client_id is specific, we might want custom accounts for this client.
        # But typically we mix or select.
        # Let's assume if client_id is passed, we filter by it.
        # If no client accounts found, maybe fall back?
        # The prompt says: "Return list of accounts ... chosen standard plan".
        # So we should filter by the criteria.

        # Logic: Get accounts where (client_id is NULL AND template_type matches) OR (client_id == requested)
        # Actually, if we use a Custom Plan, we probably only want the Custom Plan accounts.
        query = query.filter(models.StandardAccount.client_id == client_id)
    else:
        # System defaults
        query = query.filter(models.StandardAccount.client_id == None, models.StandardAccount.template_type == template_type)

    return query.all()

@router.post("/{engagement_id}/set-standard")
def set_engagement_standard(
    engagement_id: int,
    chart_mode: str = Query(..., regex="^(standard_auditflow|client_custom)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    engagement.chart_mode = chart_mode
    db.commit()
    return {"message": "Engagement chart mode updated", "chart_mode": chart_mode}

@router.post("/{engagement_id}/save-as-standard")
def save_as_standard(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Takes the accounts from the uploaded transactions/trial balance for this engagement
    and creates a Custom Standard Chart of Accounts for the Client.
    """
    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # We need to find unique accounts in this engagement.
    # We can check TrialBalanceEntry (if used) or Transactions.
    # Assuming Transactions for now as per Engagement model relations, or TrialBalanceEntry if we had it exposed.
    # The prompt mentions "upload trial balance" logic uses `TrialBalanceIngestion`.
    # But usually ingestion persists to `Transaction` or `TrialBalanceEntry`.
    # Let's assume we use `Transaction` distinct account codes.

    # Wait, `TrialBalanceEntry` is in memory but not in `models.py` I read earlier?
    # Let's check `models.py` again. I might have missed it or it's not there.
    # `models.py` content I read earlier ends with `Payment`.
    # `Transaction` has `account_code` and `account_name`.

    transactions = db.query(models.Transaction.account_code, models.Transaction.account_name)\
        .filter(models.Transaction.engagement_id == engagement_id)\
        .distinct().all()

    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions found to generate standard chart.")

    count = 0
    for code, name in transactions:
        if not code: continue

        # Check if already exists for this client
        existing = db.query(models.StandardAccount).filter(
            models.StandardAccount.client_id == engagement.client_id,
            models.StandardAccount.code == code
        ).first()

        if not existing:
            new_std = models.StandardAccount(
                code=code,
                name=name or "Unknown",
                type="Custom", # We might need to infer or let user edit later
                template_type=f"custom_{engagement.client_id}",
                client_id=engagement.client_id,
                level=1 # Default
            )
            db.add(new_std)
            count += 1

    db.commit()

    # Auto-switch mode
    engagement.chart_mode = "client_custom"
    db.commit()

    return {"message": f"Created {count} custom standard accounts for Client ID {engagement.client_id}"}


@router.get("/{engagement_id}", response_model=dict)
def get_mapping_context(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # 1. Get Client Accounts (from transactions)
    # Group by code to get unique list
    # Use SQLAlchemy to get distinct
    client_accounts_query = db.query(
        models.Transaction.account_code,
        models.Transaction.account_name
    ).filter(models.Transaction.engagement_id == engagement_id).distinct()

    client_accounts = [{"code": r.account_code, "name": r.account_name} for r in client_accounts_query.all() if r.account_code]

    # 2. Get Standard Accounts based on mode
    if engagement.chart_mode == "client_custom":
        std_accounts_query = db.query(models.StandardAccount).filter(
            models.StandardAccount.client_id == engagement.client_id
        ).all()
    else:
        # Default AuditFlow (BR GAAP)
        std_accounts_query = db.query(models.StandardAccount).filter(
            models.StandardAccount.client_id == None,
            models.StandardAccount.template_type == "br_gaap" # or engagement.service_type if it matches
        ).all()

    # Convert to Pydantic models explicitly to avoid serialization issues
    std_accounts = [schemas.StandardAccountRead.model_validate(acc) for acc in std_accounts_query]

    # 3. Get Existing Mappings
    # Mappings are by Firm. But we should try to match by client_account_code.
    mappings_query = db.query(models.AccountMapping).filter(
        models.AccountMapping.firm_id == current_user.firm_id
    ).all()

    # Explicit conversion
    mappings = [schemas.AccountMappingRead.model_validate(m) for m in mappings_query]

    return {
        "client_accounts": client_accounts,
        "standard_accounts": std_accounts,
        "mappings": mappings,
        "chart_mode": engagement.chart_mode
    }

@router.post("/map", response_model=schemas.AccountMappingRead)
def create_mapping(
    mapping: schemas.AccountMappingBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if standard account exists
    std_account = db.query(models.StandardAccount).filter(models.StandardAccount.id == mapping.standard_account_id).first()
    if not std_account:
        raise HTTPException(status_code=404, detail="Standard Account not found")

    # Create or Update Mapping for this firm
    # Logic: If client_account_code is provided, prioritize it.

    if mapping.client_account_code:
        existing = db.query(models.AccountMapping).filter(
            models.AccountMapping.firm_id == current_user.firm_id,
            models.AccountMapping.client_account_code == mapping.client_account_code
        ).first()
    else:
        existing = db.query(models.AccountMapping).filter(
            models.AccountMapping.firm_id == current_user.firm_id,
            models.AccountMapping.client_description == mapping.client_description
        ).first()

    if existing:
        existing.standard_account_id = mapping.standard_account_id
        # Update other fields to ensure consistency
        if mapping.client_account_code:
             existing.client_account_code = mapping.client_account_code
        if mapping.client_description:
             existing.client_description = mapping.client_description

        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_mapping = models.AccountMapping(
            firm_id=current_user.firm_id,
            client_description=mapping.client_description,
            client_account_code=mapping.client_account_code,
            standard_account_id=mapping.standard_account_id
        )
        db.add(new_mapping)
        db.commit()
        db.refresh(new_mapping)
        return new_mapping

@router.get("/firm-mappings", response_model=List[schemas.AccountMappingRead])
def list_firm_mappings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.AccountMapping).filter(
        models.AccountMapping.firm_id == current_user.firm_id
    ).all()

@router.post("/upload-trial-balance", response_model=List[str])
def analyze_trial_balance(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Parses a Trial Balance (CSV/Excel) and returns a list of account descriptions
    that are NOT yet mapped for this firm.
    """
    try:
        df = TrialBalanceIngestion.read_file(file)
        result = TrialBalanceIngestion.validate_and_parse(df)

        if not result["valid"]:
             raise HTTPException(status_code=400, detail=f"Invalid file structure: {', '.join(result['errors'])}")

        unique_accounts = result["unique_accounts"]

        # Get existing mappings for firm (by description or code if available in parse result)
        # Note: validate_and_parse returns descriptions list in unique_accounts.

        existing_mappings = db.query(models.AccountMapping.client_description).filter(
            models.AccountMapping.firm_id == current_user.firm_id
        ).all()
        mapped_set = {m[0] for m in existing_mappings}

        # Filter unmapped
        unmapped = [acc for acc in unique_accounts if acc not in mapped_set]
        return unmapped

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.post("/bulk-map", status_code=status.HTTP_201_CREATED)
def bulk_create_mapping(
    mappings: List[schemas.AccountMappingBase],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    count = 0
    for mapping in mappings:
        # Prioritize Code mapping
        existing = None
        if mapping.client_account_code:
            existing = db.query(models.AccountMapping).filter(
                models.AccountMapping.firm_id == current_user.firm_id,
                models.AccountMapping.client_account_code == mapping.client_account_code
            ).first()

        if not existing:
             existing = db.query(models.AccountMapping).filter(
                models.AccountMapping.firm_id == current_user.firm_id,
                models.AccountMapping.client_description == mapping.client_description
            ).first()

        if existing:
            existing.standard_account_id = mapping.standard_account_id
            if mapping.client_account_code:
                existing.client_account_code = mapping.client_account_code
        else:
            new_mapping = models.AccountMapping(
                firm_id=current_user.firm_id,
                client_description=mapping.client_description,
                client_account_code=mapping.client_account_code,
                standard_account_id=mapping.standard_account_id
            )
            db.add(new_mapping)
        count += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to save mappings: {str(e)}")

    return {"message": f"Successfully processed {count} mappings"}
