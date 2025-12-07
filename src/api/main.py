from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os

from src.api.database import engine, Base
from src.api import models
from src.api.logging_config import setup_logging
from prometheus_fastapi_instrumentator import Instrumentator

# Import Routes
from src.api.routes import (
    auth,
    register,
    clients,
    engagements,
    analysis,
    mapping,
    planning,
    circularization,
    acceptance,
    team,
    sampling,
    payroll,
    workpapers,
    billing,
    financial_statements,
    reconciliation,
    analytics,
    cleaning
)

# Create Tables
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield

app = FastAPI(title="AuditFlow API", version="1.0.0", lifespan=lifespan)

# CORS
# Allow all for development/demo ease
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monitoring
Instrumentator().instrument(app).expose(app)

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
app.include_router(financial_statements.router)
app.include_router(reconciliation.router)
app.include_router(analytics.router, prefix="/analyze", tags=["Analytics"])
app.include_router(cleaning.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AuditFlow API"}
