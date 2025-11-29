from src.api.celery_app import celery_app
from src.api.database import SessionLocal
from src.api import models
from src.scripts.benford_analysis import calculate_benford
from src.scripts.duplicate_analysis import find_duplicates

@celery_app.task
def task_run_benford(engagement_id: int, user_id: int):
    db = SessionLocal()
    try:
        engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
        if not engagement:
            return {"error": "Engagement not found"}

        values = [t.amount for t in engagement.transactions if t.amount is not None]
        if not values:
             return {"error": "No transactions"}

        result = calculate_benford(values)

        db_result = models.AnalysisResult(
            engagement_id=engagement.id,
            test_type="benford",
            result=result,
            executed_by_user_id=user_id
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return {"status": "completed", "result_id": db_result.id}
    finally:
        db.close()

@celery_app.task
def task_run_duplicates(engagement_id: int, user_id: int):
    db = SessionLocal()
    try:
        engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
        if not engagement:
             return {"error": "Engagement not found"}

        transactions_dicts = [
            {"id": t.id, "vendor": t.vendor, "amount": t.amount, "date": str(t.date) if t.date else None}
            for t in engagement.transactions
        ]

        result = find_duplicates(transactions_dicts)

        db_result = models.AnalysisResult(
            engagement_id=engagement.id,
            test_type="duplicates",
            result={"duplicates": result},
            executed_by_user_id=user_id
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return {"status": "completed", "result_id": db_result.id}
    finally:
        db.close()
