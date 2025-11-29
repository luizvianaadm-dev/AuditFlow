from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from src.scripts.benford_analysis import calculate_benford
from src.scripts.duplicate_analysis import find_duplicates
from src.api.database import engine, Base
from src.api import models  # Import models to register them with Base
from src.api.routes import clients, auth, register, engagements, analysis, mapping, planning

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AuditFlow API")

# CORS Middleware (Allow React Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(register.router)
app.include_router(clients.router)
app.include_router(engagements.router)
app.include_router(analysis.router)
app.include_router(mapping.router)
app.include_router(planning.router)

class TransactionList(BaseModel):
    values: List[float]

class Transaction(BaseModel):
    id: Optional[Any] = None
    vendor: str
    amount: float
    date: Optional[str] = None

class TransactionInput(BaseModel):
    transactions: List[Transaction]

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

@app.post("/analyze/duplicates")
async def analyze_duplicates(data: TransactionInput) -> List[Dict[str, Any]]:
    """
    Analyzes a list of transactions to find potential duplicates
    based on exact amount and fuzzy vendor name matching.
    """
    # Convert Pydantic models to list of dicts for the logic function
    transactions_dicts = [tx.model_dump() for tx in data.transactions]

    duplicates = find_duplicates(transactions_dicts)
    return duplicates
