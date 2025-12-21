from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Any

from src.api.database import get_db
from src.api import models
from src.api.deps import get_current_user

router = APIRouter(prefix="/billing", tags=["billing"])

def seed_plans(db: Session):
    if db.query(models.Plan).count() == 0:
        plans = [
            models.Plan(
                name="Basic",
                price=99.00,
                description="Para auditores individuais iniciando a jornada digital.",
                features=["Até 5 Clientes", "Relatórios em PDF", "Suporte por Email", "Análise de Benford"]
            ),
            models.Plan(
                name="Pro",
                price=299.00,
                description="Para pequenas firmas em crescimento.",
                features=["Clientes Ilimitados", "Relatórios PDF/Word/Excel", "Múltiplos Usuários (Até 5)", "Suporte Prioritário", "Análise de Duplicatas"]
            ),
            models.Plan(
                name="Enterprise",
                price=999.00,
                description="Para grandes organizações e redes de auditoria.",
                features=["Tudo do Pro", "Usuários Ilimitados", "API Dedicada", "SSO / 2FA", "Gerente de Conta"]
            )
        ]
        db.add_all(plans)
        db.commit()

@router.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    seed_plans(db)
    return db.query(models.Plan).all()

@router.get("/my-subscription")
def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    sub = db.query(models.Subscription).filter(models.Subscription.firm_id == current_user.firm_id).first()

    payments = []
    if sub:
        payments = db.query(models.Payment).filter(models.Payment.subscription_id == sub.id).order_by(models.Payment.date.desc()).all()

    return {
        "subscription": sub,
        "plan": sub.plan if sub else None,
        "payments": payments
    }

@router.post("/subscribe")
async def subscribe(
    data: dict, # { plan_id: int }
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    plan_id = data.get('plan_id')

    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    sub = db.query(models.Subscription).filter(models.Subscription.firm_id == current_user.firm_id).first()

    if sub:
        sub.plan_id = plan.id
        sub.status = "active"
        sub.current_period_end = datetime.utcnow() + timedelta(days=30)
    else:
        sub = models.Subscription(
            firm_id=current_user.firm_id,
            plan_id=plan.id,
            status="active",
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)

    # Asaas Integration
    from src.api.services import asaas
    firm = db.query(models.AuditFirm).filter(models.AuditFirm.id == current_user.firm_id).first()
    
    # 1. Create/Get Customer
    customer_id = await asaas.create_customer(firm.name, current_user.email, firm.cnpj)
    
    # 2. Create Payment
    payment_url = await asaas.create_payment(
        customer_id=customer_id,
        value=plan.price,
        description=f"Assinatura AuditFlow - Plano {plan.name}"
    )

    # Record Payment (Pending)
    payment = models.Payment(
        subscription_id=sub.id,
        amount=plan.price,
        status="pending", # Wait for webhook (not impl yet) or user return
        invoice_url=payment_url
    )
    db.add(payment)
    db.commit()

    return {"message": "Subscription initiated", "plan": plan.name, "paymentUrl": payment_url}
