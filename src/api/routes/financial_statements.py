from fastapi import APIRouter, Depends, HTTPException, Body
+from sqlalchemy.orm import Session
+from sqlalchemy import func
+from typing import Any, Dict
+from datetime import datetime
+
+from src.api.database import get_db
+from src.api import models, schemas
+from src.api.deps import get_current_user
+
+router = APIRouter(
+    prefix="/engagements/{engagement_id}/fs",
+    tags=["financial-statements"]
+)
+
+@router.get("/context")
+def get_fs_context(
+    engagement_id: int,
+    db: Session = Depends(get_db),
+    current_user: models.User = Depends(get_current_user)
+):
+    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
+    if not engagement:
+        raise HTTPException(status_code=404, detail="Engagement not found")
+
+    context = db.query(models.FinancialStatementContext).filter(
+        models.FinancialStatementContext.engagement_id == engagement_id
+    ).first()
+
+    if not context:
+        # Initialize empty context
+        context = models.FinancialStatementContext(
+            engagement_id=engagement_id,
+            context_data={},
+            status="draft"
+        )
+        db.add(context)
+        db.commit()
+        db.refresh(context)
+
+    return context
+
+@router.put("/context")
+def update_fs_context(
+    engagement_id: int,
+    context_data: Dict[str, Any] = Body(...),
+    db: Session = Depends(get_db),
+    current_user: models.User = Depends(get_current_user)
+):
+    context = db.query(models.FinancialStatementContext).filter(
+        models.FinancialStatementContext.engagement_id == engagement_id
+    ).first()
+
+    if not context:
+        context = models.FinancialStatementContext(
+            engagement_id=engagement_id,
+            context_data=context_data,
+            status="draft"
+        )
+        db.add(context)
+    else:
+        context.context_data = context_data
+        context.updated_at = datetime.utcnow()
+
+    db.commit()
+    db.refresh(context)
+    return context
+
+@router.get("/generate")
+def generate_financial_statements(
+    engagement_id: int,
+    db: Session = Depends(get_db),
+    current_user: models.User = Depends(get_current_user)
+):
+    """
+    Generates the Financial Statements (Block 6+ of the prompt) based on Mapped Accounts.
+    """
+    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
+    if not engagement:
+        raise HTTPException(status_code=404, detail="Engagement not found")
+
+    # 1. Get Mappings
+    mappings = db.query(models.AccountMapping).filter(
+        models.AccountMapping.firm_id == current_user.firm_id
+    ).all()
+
+    # Map by Client Code -> Standard ID
+    mapping_dict = {m.client_account_code: m.standard_account_id for m in mappings if m.client_account_code}
+
+    # 2. Get Transaction Data (Aggregated by Account Code)
+    # We assume 'Transaction' table is the source of truth for now.
+    # Group by account_code
+    balances = db.query(
+        models.Transaction.account_code,
+        models.Transaction.account_name,
+        func.sum(models.Transaction.amount).label("final_balance")
+    ).filter(
+        models.Transaction.engagement_id == engagement_id
+    ).group_by(models.Transaction.account_code, models.Transaction.account_name).all()
+
+    # 3. Aggregate by Standard Account
+    # Structure: standard_account_code -> total
+    std_balances = {}
+
+    # Pre-fetch standard accounts to know their codes and types
+    if engagement.chart_mode == "client_custom":
+        std_accs = db.query(models.StandardAccount).filter(models.StandardAccount.client_id == engagement.client_id).all()
+    else:
+        std_accs = db.query(models.StandardAccount).filter(models.StandardAccount.template_type == "br_gaap").all()
+
+    std_map = {sa.id: sa for sa in std_accs}
+
+    for code, name, balance in balances:
+        if code in mapping_dict:
+            std_id = mapping_dict[code]
+            if std_id in std_map:
+                std_code = std_map[std_id].code
+                std_balances[std_code] = std_balances.get(std_code, 0.0) + (balance or 0.0)
+
+    # 4. Construct BP and DRE
+    # This requires mapping Standard Codes (e.g. "1.1.01") to Report Lines (e.g. "Caixa e Equivalentes").
+    # Assuming Standard Plan matches Report Structure:
+
+    # Helper to sum by prefix
+    def get_bal(prefix):
+        total = 0.0
+        for k, v in std_balances.items():
+            if k.startswith(prefix):
+                total += v
+        return total
+
+    # Balanço Patrimonial (Simplificado para MVP)
+    bp = {
+        "ativo": {
+            "circulante": get_bal("1.1"),
+            "nao_circulante": get_bal("1.2"),
+            "total": get_bal("1")
+        },
+        "passivo": {
+            "circulante": get_bal("2.1"),
+            "nao_circulante": get_bal("2.2"),
+            "patrimonio_liquido": get_bal("2.3"),
+            "total": get_bal("2")
+        }
+    }
+
+    # DRE
+    # Revenue (Class 3) is Credit usually, so negative in DB if using standard double entry?
+    # Assuming Transactions store: Debit +, Credit -.
+    # Revenue (Credit) -> Negative. Expense (Debit) -> Positive.
+    # We typically invert for reporting.
+
+    receita = -1 * get_bal("3")
+    despesa = get_bal("4")
+    lucro = receita - despesa # Simplified
+
+    dre = {
+        "receita_liquida": receita,
+        "lucro_bruto": receita, # Minus CPV if mapped
+        "despesas_operacionais": despesa,
+        "lucro_liquido": lucro
+    }
+
+    # Validation: Ativo = Passivo + PL
+    validations = {
+        "integridade": abs(bp["ativo"]["total"] - (bp["passivo"]["total"] * -1)) < 0.01 # Assuming Passivo stored as negative?
+    }
+
+    # If Passivo is stored as negative (Credit), then Total Passivo + PL should be negative.
+    # Ativo (Positive) + Passivo (Negative) = 0.
+    # Let's check logic:
+    # 1 (Asset): Debit (+).
+    # 2 (Liability): Credit (-).
+    # Sum of all should be 0.
+    total_check = get_bal("1") + get_bal("2") + get_bal("3") + get_bal("4")
+
+    validations["balance_check"] = abs(total_check) < 0.01
+
+    return {
+        "demonstracoes": {
+            "balanco_patrimonial": bp,
+            "dre": dre
+        },
+        "validacoes": validations,
+        "indicadores": {
+            "margem_liquida": (lucro / receita) if receita else 0
+        }
+    }
