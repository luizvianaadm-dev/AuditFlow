from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
import os
from pydantic import BaseModel
from src.scripts.benford_analysis import calculate_benford
from src.scripts.duplicate_analysis import find_duplicates
from src.api.database import engine, Base
from src.api import models  # Import models to register them with Base
from src.api.routes import clients, auth, register, engagements, analysis, mapping, planning, circularization, acceptance, team, sampling, payroll, workpapers, billing, certificates, cleaning
from src.api.logging_config import setup_logging
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager

# Create tables
# Base.metadata.create_all(bind=engine)  # Commented out to use Alembic migrations

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield

app = FastAPI(title="AuditFlow API", lifespan=lifespan)

# Setup Prometheus Metrics
Instrumentator().instrument(app).expose(app)

# CORS Middleware (Allow React Frontend)
origins = []

# 1. Try to read FRONTEND_URL
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

# 2. Try to read URL_FRONTEND (fallback)
url_frontend = os.getenv("URL_FRONTEND")
if url_frontend:
    origins.append(url_frontend)

# 3. If none found, use localhost
if not origins:
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
app.include_router(circularization.router)
app.include_router(acceptance.router)
app.include_router(team.router)
app.include_router(sampling.router)
app.include_router(payroll.router)
app.include_router(workpapers.router)
app.include_router(billing.router)
app.include_router(certificates.router)
app.include_router(cleaning.router)

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
