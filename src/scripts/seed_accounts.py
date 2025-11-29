from sqlalchemy.orm import Session
from src.api.database import SessionLocal, engine
from src.api import models

def seed_standard_accounts():
    db = SessionLocal()

    # Check if already seeded
    if db.query(models.StandardAccount).first():
        print("Standard accounts already seeded.")
        db.close()
        return

    accounts = [
        # Ativo
        {"code": "1", "name": "ATIVO", "type": "Asset"},
        {"code": "1.1", "name": "ATIVO CIRCULANTE", "type": "Asset"},
        {"code": "1.1.01", "name": "Caixa e Equivalentes de Caixa", "type": "Asset"},
        {"code": "1.1.02", "name": "Contas a Receber", "type": "Asset"},
        {"code": "1.1.03", "name": "Estoques", "type": "Asset"},
        {"code": "1.2", "name": "ATIVO NÃO CIRCULANTE", "type": "Asset"},
        {"code": "1.2.01", "name": "Realizável a Longo Prazo", "type": "Asset"},
        {"code": "1.2.02", "name": "Investimentos", "type": "Asset"},
        {"code": "1.2.03", "name": "Imobilizado", "type": "Asset"},
        {"code": "1.2.04", "name": "Intangível", "type": "Asset"},

        # Passivo
        {"code": "2", "name": "PASSIVO", "type": "Liability"},
        {"code": "2.1", "name": "PASSIVO CIRCULANTE", "type": "Liability"},
        {"code": "2.1.01", "name": "Fornecedores", "type": "Liability"},
        {"code": "2.1.02", "name": "Obrigações Trabalhistas", "type": "Liability"},
        {"code": "2.1.03", "name": "Obrigações Tributárias", "type": "Liability"},
        {"code": "2.2", "name": "PASSIVO NÃO CIRCULANTE", "type": "Liability"},
        {"code": "2.2.01", "name": "Empréstimos e Financiamentos", "type": "Liability"},
        {"code": "2.3", "name": "PATRIMÔNIO LÍQUIDO", "type": "Equity"},
        {"code": "2.3.01", "name": "Capital Social", "type": "Equity"},
        {"code": "2.3.02", "name": "Reservas de Lucros", "type": "Equity"},

        # Resultado
        {"code": "3", "name": "RECEITAS", "type": "Revenue"},
        {"code": "3.1", "name": "Receita Operacional Bruta", "type": "Revenue"},
        {"code": "4", "name": "CUSTOS E DESPESAS", "type": "Expense"},
        {"code": "4.1", "name": "Custo das Mercadorias Vendidas", "type": "Expense"},
        {"code": "4.2", "name": "Despesas Operacionais", "type": "Expense"},
        {"code": "4.2.01", "name": "Despesas Administrativas", "type": "Expense"},
        {"code": "4.2.02", "name": "Despesas com Vendas", "type": "Expense"},
        {"code": "4.2.03", "name": "Despesas Financeiras", "type": "Expense"},
    ]

    for acc in accounts:
        db_acc = models.StandardAccount(code=acc["code"], name=acc["name"], type=acc["type"])
        db.add(db_acc)

    db.commit()
    print("Standard accounts seeded successfully.")
    db.close()

if __name__ == "__main__":
    # Create tables if not exist (e.g. running manually)
    models.Base.metadata.create_all(bind=engine)
    seed_standard_accounts()
