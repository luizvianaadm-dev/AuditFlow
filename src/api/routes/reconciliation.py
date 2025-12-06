from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import pandas as pd
import io
from src.scripts.reconciliation_engine import ReconciliationEngine
from src.api.deps import get_current_user
from src.api import models

router = APIRouter(
    prefix="/analyze",
    tags=["analysis"]
)

@router.post("/reconciliation")
async def reconcile_files(
    bank_file: UploadFile = File(...),
    financial_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    """
    Analyzes Bank Statement vs Financial Records to find subset matches.
    """
    try:
        # Read files
        if bank_file.filename.endswith('.csv'):
            bank_df = pd.read_csv(bank_file.file)
        elif bank_file.filename.endswith(('.xls', '.xlsx')):
            bank_df = pd.read_excel(bank_file.file)
        else:
            raise HTTPException(status_code=400, detail="Bank file must be CSV or Excel")

        if financial_file.filename.endswith('.csv'):
            fin_df = pd.read_csv(financial_file.file)
        elif financial_file.filename.endswith(('.xls', '.xlsx')):
            fin_df = pd.read_excel(financial_file.file)
        else:
            raise HTTPException(status_code=400, detail="Financial file must be CSV or Excel")

        # Process
        results = ReconciliationEngine.process_reconciliation(bank_df, fin_df)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
