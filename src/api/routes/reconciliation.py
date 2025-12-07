from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import shutil
import os
import uuid
import logging
from src.scripts.reconciliation_engine import ReconciliationEngine

router = APIRouter(
    prefix="/analyze",
    tags=["analysis"]
)

TMP_DIR = "/tmp/auditflow_uploads"
os.makedirs(TMP_DIR, exist_ok=True)

logger = logging.getLogger(__name__)

def run_reconciliation_task(bank_path: str, fin_path: str, output_path: str):
    try:
        logger.info(f"Starting reconciliation task. Output: {output_path}")
        ReconciliationEngine.process_reconciliation(bank_path, fin_path, output_path)
        logger.info(f"Reconciliation task completed. Result saved to {output_path}")
    except Exception as e:
        logger.error(f"Reconciliation task failed: {str(e)}")
    finally:
        # Cleanup input files
        try:
            if os.path.exists(bank_path): os.remove(bank_path)
            if os.path.exists(fin_path): os.remove(fin_path)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup files: {cleanup_error}")

@router.post("/reconciliation")
async def analyze_reconciliation(
    background_tasks: BackgroundTasks,
    bank_file: UploadFile = File(...),
    financial_file: UploadFile = File(...)
):
    """
    Async endpoint for reconciliation analysis.
    Returns task_id immediately.
    """
    try:
        task_id = str(uuid.uuid4())
        # Sanitization of filename is good practice but for internal use, trusting basic uuid prefix
        bank_filename = os.path.basename(bank_file.filename)
        fin_filename = os.path.basename(financial_file.filename)

        bank_path = os.path.join(TMP_DIR, f"{task_id}_bank_{bank_filename}")
        fin_path = os.path.join(TMP_DIR, f"{task_id}_fin_{fin_filename}")
        output_path = os.path.join(TMP_DIR, f"{task_id}_result.json")

        # Save uploads
        with open(bank_path, "wb") as buffer:
            shutil.copyfileobj(bank_file.file, buffer)
        with open(fin_path, "wb") as buffer:
            shutil.copyfileobj(financial_file.file, buffer)

        # Queue Task
        background_tasks.add_task(run_reconciliation_task, bank_path, fin_path, output_path)

        return {
            "status": "processing",
            "message": "Análise iniciada.",
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
