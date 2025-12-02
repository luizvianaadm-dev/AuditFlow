from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from src.scripts.data_cleaning import DataCleaner
from src.api.deps import get_current_user
from src.api.models import User
import io
import pandas as pd

router = APIRouter(
    prefix="/cleaning",
    tags=["cleaning"]
)

@router.post("/preview")
async def preview_cleaned_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    cleaner = DataCleaner(content, file.filename)

    try:
        preview_df = cleaner.process()

        # Prepare response
        return {
            "columns": list(preview_df.columns),
            "preview": preview_df.to_dict(orient='records'),
            "total_rows": len(cleaner.df) if cleaner.df is not None else 0,
            "detected_encoding": cleaner.encoding,
            "detected_separator": cleaner.separator
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning data: {str(e)}")

@router.post("/download")
async def download_cleaned_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Re-processes the file and returns the full cleaned CSV.
    (In a real app, we might cache the result of 'preview' to avoid re-uploading,
     but for this stateless MVP, re-upload is simpler).
    """
    content = await file.read()
    cleaner = DataCleaner(content, file.filename)
    cleaner.process()

    if cleaner.df is None or cleaner.df.empty:
         raise HTTPException(status_code=400, detail="Resulting dataframe is empty.")

    # Export to CSV
    stream = io.StringIO()
    cleaner.df.to_csv(stream, sep=';', index=False, decimal=',')

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=cleaned_{file.filename}"
    return response
