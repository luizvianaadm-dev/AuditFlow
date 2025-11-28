from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import Dict, List, Any
from pydantic import BaseModel
from src.scripts.benford_analysis import calculate_benford

app = FastAPI(title="AuditFlow API")

class TransactionList(BaseModel):
    values: List[float]

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify service status.
    """
    return {"status": "ok", "service": "AuditFlow API"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    Dummy endpoint to handle file uploads.
    """
    if not file.filename:
        return {"message": "No filename provided"}

    return {"filename": file.filename, "message": "File received"}

@app.post("/analyze/benford")
async def analyze_benford(data: TransactionList) -> Dict[str, Any]:
    """
    Analyzes a list of transaction values using Benford's Law.
    """
    if not data.values:
        raise HTTPException(status_code=400, detail="The list of values cannot be empty.")

    result = calculate_benford(data.values)
    return result
