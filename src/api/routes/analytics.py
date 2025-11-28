from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from src.scripts.benford_analysis import calculate_benford
from src.scripts.duplicate_analysis import find_duplicates
from typing import List, Optional

router = APIRouter()

class BenfordRequest(BaseModel):
    transactions: list[float] = Field(..., description="List of monetary values to analyze")

class TransactionItem(BaseModel):
    id: Optional[str | int] = None
    amount: float
    vendor: str
    date: Optional[str] = None

class DuplicateRequest(BaseModel):
    transactions: List[TransactionItem] = Field(..., description="List of transactions to check for duplicates")

@router.post("/benford")
async def analyze_benford(request: BenfordRequest) -> dict:
    """
    Analyzes a list of transactions using Benford's Law.
    Returns expected vs observed frequencies and anomalies.
    """
    if not request.transactions:
        raise HTTPException(status_code=400, detail="Transaction list cannot be empty")

    # Check if there are valid non-zero values?
    # calculate_benford handles zeros gracefully, but if result is empty maybe warn?
    # For now, let's trust calculate_benford.

    try:
        result = calculate_benford(request.transactions)
    except Exception as e:
        # Catch unexpected errors from the script
        raise HTTPException(status_code=500, detail=str(e))

    return result

@router.post("/duplicates")
async def analyze_duplicates(request: DuplicateRequest) -> dict:
    """
    Identifies potential duplicate payments.
    """
    if not request.transactions:
        raise HTTPException(status_code=400, detail="Transaction list cannot be empty")

    try:
        # Convert Pydantic models to dicts
        tx_list = [t.model_dump() for t in request.transactions]
        duplicates = find_duplicates(tx_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"suspicious_groups": duplicates}
