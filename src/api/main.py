from fastapi import FastAPI, UploadFile, File
from typing import Dict
from src.api.routes import analytics

app = FastAPI(
    title="AuditFlow API",
    description="API for AuditFlow Platform",
    version="0.1.0"
)

app.include_router(analytics.router, prefix="/analyze", tags=["Analytics"])

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the service status.
    """
    return {"status": "ok", "service": "AuditFlow API"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    Dummy endpoint to handle file uploads.
    """
    return {"filename": file.filename or "unknown", "status": "received"}
