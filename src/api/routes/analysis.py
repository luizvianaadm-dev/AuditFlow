from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from src.api.database import get_db
from src.api import models, schemas
from src.api.deps import get_current_user
from src.scripts.benford_analysis import calculate_benford
from src.scripts.duplicate_analysis import find_duplicates
from src.scripts.pdf_generator import generate_audit_report
from src.scripts.docx_generator import generate_audit_report_docx
from src.scripts.export_utils import export_to_excel, export_to_csv, benford_to_df, duplicates_to_df, transactions_to_df, mistatements_to_df
from celery.result import AsyncResult
from src.api.tasks import task_run_benford, task_run_duplicates

router = APIRouter(
    prefix="/engagements",
    tags=["analysis"]
)

@router.post("/{engagement_id}/run-benford", status_code=status.HTTP_202_ACCEPTED)
def run_benford_analysis(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Engagement belongs to user's firm
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    task = task_run_benford.delay(engagement_id, current_user.id)
    return {"task_id": task.id}

@router.post("/{engagement_id}/run-duplicates", status_code=status.HTTP_202_ACCEPTED)
def run_duplicate_analysis(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify Engagement belongs to user's firm
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    task = task_run_duplicates.delay(engagement_id, current_user.id)
    return {"task_id": task.id}

@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }

@router.get("/{engagement_id}/results", response_model=List[schemas.AnalysisResultRead])
def read_analysis_results(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    return db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement.id
    ).order_by(models.AnalysisResult.executed_at.desc()).all()

@router.get("/{engagement_id}/report", response_class=StreamingResponse)
def download_audit_report(
    engagement_id: int,
    format: str = Query('pdf', enum=['pdf', 'docx']),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Fetch Engagement (with client info)
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    # 2. Fetch Analysis History
    results = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.engagement_id == engagement.id
    ).order_by(models.AnalysisResult.executed_at.desc()).all()

    # 3. Fetch Mistatements Summary
    mistatements = db.query(models.Mistatement).filter(
        models.Mistatement.engagement_id == engagement.id
    ).all()

    mistatement_summary = {
        "items": mistatements,
        "total_adjusted": sum(m.amount_divergence for m in mistatements if m.status == 'adjusted'),
        "total_unadjusted": sum(m.amount_divergence for m in mistatements if m.status in ['open', 'unadjusted'])
    }

    # 4. Generate Document
    filename_base = f"Relatorio_Auditoria_{engagement.client.name.replace(' ', '_')}_{engagement.year}"

    if format == 'docx':
        buffer = generate_audit_report_docx(engagement, results, mistatement_summary)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{filename_base}.docx"
    else:
        buffer = generate_audit_report(engagement, results, mistatement_summary)
        media_type = "application/pdf"
        filename = f"{filename_base}.pdf"

    # 5. Return Stream
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/{engagement_id}/export/{export_type}")
def export_data(
    engagement_id: int,
    export_type: str, # benford, duplicates, transactions, mistatements
    format: str = Query('xlsx', enum=['xlsx', 'csv']),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    engagement = db.query(models.Engagement).join(models.Client).filter(
        models.Engagement.id == engagement_id,
        models.Client.firm_id == current_user.firm_id
    ).first()

    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")

    df = None
    filename_base = f"{export_type}_{engagement.name}"

    if export_type == 'transactions':
        df = transactions_to_df(engagement.transactions)

    elif export_type == 'mistatements':
         mistatements = db.query(models.Mistatement).filter(models.Mistatement.engagement_id == engagement.id).all()
         df = mistatements_to_df(mistatements)

    elif export_type in ['benford', 'duplicates']:
        # Fetch latest result
        result = db.query(models.AnalysisResult).filter(
            models.AnalysisResult.engagement_id == engagement.id,
            models.AnalysisResult.test_type == export_type
        ).order_by(models.AnalysisResult.executed_at.desc()).first()

        if not result:
            raise HTTPException(status_code=404, detail=f"No {export_type} analysis found")

        if export_type == 'benford':
            df = benford_to_df(result.result)
        else:
            df = duplicates_to_df(result.result)

    else:
        raise HTTPException(status_code=400, detail="Invalid export type")

    if df is None or df.empty:
         # Return empty CSV/Excel instead of 404? Or just empty DF logic handled by utils?
         # If df is empty, export_utils should handle it (create headers but no data)
         pass

    # Export
    if format == 'csv':
        buffer = export_to_csv(df)
        media_type = "text/csv"
        filename = f"{filename_base}.csv"
    else:
        buffer = export_to_excel([df], sheet_names=[export_type.capitalize()])
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{filename_base}.xlsx"

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
