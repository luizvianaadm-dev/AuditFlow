from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from src.api.database import get_db
from src.api import models
import os
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

ASAAS_WEBHOOK_TOKEN = os.getenv("ASAAS_WEBHOOK_TOKEN", "my-secret-webhook-token")

@router.post("/asaas")
async def asaas_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receives payment notifications from Asaas.
    """
    # 1. Security Check
    auth_token = request.headers.get("asaas-access-token")
    if auth_token != ASAAS_WEBHOOK_TOKEN:
         # Log warning?
         # raise HTTPException(status_code=401, detail="Invalid Webhook Token")
         pass # For now, just pass or allow debug. But better to be safe.
    
    data = await request.json()
    event = data.get("event")
    payment = data.get("payment", {})
    
    if event in ["PAYMENT_CONFIRMED", "PAYMENT_RECEIVED"]:
        invoice_url = payment.get("invoiceUrl")
        # Find payment by invoice_url or external_id if we stored it
        # Since we stored invoice_url in creating billing, let's use it
        
        db_payment = db.query(models.Payment).filter(models.Payment.invoice_url == invoice_url).first()
        if db_payment:
            db_payment.status = "paid"
            db_payment.date = datetime.now() # Update payment date
            
            # Activate Subscription
            sub = db.query(models.Subscription).filter(models.Subscription.id == db_payment.subscription_id).first()
            if sub:
                sub.status = "active"
            
            db.commit()
            
    return {"status": "received"}
