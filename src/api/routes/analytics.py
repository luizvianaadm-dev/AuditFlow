from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from src.scripts.benford_analysis import calculate_benford

router = APIRouter()

class BenfordRequest(BaseModel):
    transactions: list[float] = Field(..., description="List of monetary values to analyze")

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
