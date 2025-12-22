from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
import pandas as pd
import io
from typing import List

router = APIRouter()

@router.post("/import", summary="Import Financial Data (Trial Balance)")
async def import_financial_data(
    engagement_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Parses a Trial Balance (Balancete) from Excel or CSV.
    Returns the raw data preview and detected columns for mapping.
    """
    contents = await file.read()
    
    try:
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(contents))
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents), encoding='utf-8') # Try utf-8 first
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use .xlsx, .xls, or .csv")
            
        # Clean data (sanitize columns)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.where(pd.notnull(df), None) # Replace NaN with None for JSON compatibility
        
        # Identification of potential columns (Heuristic)
        # This acts as the 'De-Para' pre-processing
        preview = df.head(10).to_dict(orient='records')
        columns = df.columns.tolist()
        
        return {
            "filename": file.filename,
            "total_rows": len(df),
            "columns": columns,
            "preview": preview,
            "message": "File parsed successfully. Please map the columns."
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
