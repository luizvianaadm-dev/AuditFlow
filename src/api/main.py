from fastapi import FastAPI, UploadFile, File
from typing import Dict

app = FastAPI(title="AuditFlow API")

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
