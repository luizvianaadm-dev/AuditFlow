from sqlalchemy.orm import Session
from src.api.database import SessionLocal, engine
from src.api import models

def seed_standard_accounts():
    db = SessionLocal()

    # Check if already seeded (any account exists)
    if db.query(models.StandardAccount).first():
        # Ideally we check per template, but for simplicity let's check count or force update logic later.
        # For now, if we have records, we skip.
        # To force update, user must drop tables.

        # Check if condo accounts exist
        condo = db.query(models.StandardAccount).filter(models.StandardAccount.template_type == "condo").first()
        if not condo:
            print("Seeding Condo accounts...")
        else:
            print("Standard accounts already seeded.")
            db.close()
            return

    accounts_br_gaap = [
        # Ativo
        {"code": "1", "name": "ATIVO", "type": "Asset", "template": "br_gaap"},
        {"code": "1.1", "name": "ATIVO CIRCULANTE", "type": "Asset", "template": "br_gaap"},
        {"code": "1.1.01", "name": "Caixa e Equivalentes de Caixa", "type": "Asset", "template": "br_gaap"},
        {"code": "1.1.02", "name": "Contas a Receber", "type": "Asset", "template": "br_gaap"},
        {"code": "1.1.03", "name": "Estoques", "type": "Asset", "template": "br_gaap"},
        {"code": "1.2", "name": "ATIVO NÃO CIRCULANTE", "type": "Asset", "template": "br_gaap"},

        # Passivo
        {"code": "2", "name": "PASSIVO", "type": "Liability", "template": "br_gaap"},
        {"code": "2.1", "name": "PASSIVO CIRCULANTE", "type": "Liability", "template": "br_gaap"},
        {"code": "2.1.01", "name": "Fornecedores", "type": "Liability", "template": "br_gaap"},
        {"code": "2.1.02", "name": "Obrigações Trabalhistas", "type": "Liability", "template": "br_gaap"},
        {"code": "2.1.03", "name": "Obrigações Tributárias", "type": "Liability", "template": "br_gaap"},
        {"code": "2.2", "name": "PASSIVO NÃO CIRCULANTE", "type": "Liability", "template": "br_gaap"},
        {"code": "2.3", "name": "PATRIMÔNIO LÍQUIDO", "type": "Equity", "template": "br_gaap"},

        # Resultado
        {"code": "3", "name": "RECEITAS", "type": "Revenue", "template": "br_gaap"},
        {"code": "4", "name": "CUSTOS E DESPESAS", "type": "Expense", "template": "br_gaap"},
    ]

    accounts_condo = [
        # Receitas (Condomínio foca em Arrecadação)
        {"code": "100", "name": "RECEITAS ORDINÁRIAS", "type": "Revenue", "template": "condo"},
        {"code": "101", "name": "Taxa de Condomínio", "type": "Revenue", "template": "condo"},
        {"code": "102", "name": "Fundo de Reserva", "type": "Revenue", "template": "condo"},
        {"code": "103", "name": "Acordos e Multas", "type": "Revenue", "template": "condo"},

        # Despesas
        {"code": "200", "name": "DESPESAS OPERACIONAIS", "type": "Expense", "template": "condo"},
        {"code": "201", "name": "Pessoal e Encargos", "type": "Expense", "template": "condo"},
        {"code": "202", "name": "Consumo (Água/Luz/Gás)", "type": "Expense", "template": "condo"},
        {"code": "203", "name": "Manutenção e Conservação", "type": "Expense", "template": "condo"},
        {"code": "204", "name": "Administrativas", "type": "Expense", "template": "condo"},

        # Disponibilidades
        {"code": "300", "name": "DISPONIBILIDADES (Caixa/Bancos)", "type": "Asset", "template": "condo"},

        # Inadimplência
        {"code": "400", "name": "CONTAS A RECEBER (Inadimplência)", "type": "Asset", "template": "condo"},
    ]

    all_accounts = accounts_br_gaap + accounts_condo

    for acc in all_accounts:
        # Check existence to avoid dupes if partially seeded
        existing = db.query(models.StandardAccount).filter_by(code=acc["code"], template_type=acc["template"]).first()
        if not existing:
            db_acc = models.StandardAccount(
                code=acc["code"],
                name=acc["name"],
                type=acc["type"],
                template_type=acc["template"]
            )
            db.add(db_acc)

    db.commit()
    print("Standard accounts seeded successfully.")
    db.close()

if __name__ == "__main__":
    # Create tables if not exist
    models.Base.metadata.create_all(bind=engine)
    seed_standard_accounts()
