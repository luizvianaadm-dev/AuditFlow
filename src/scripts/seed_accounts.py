from sqlalchemy.orm import Session
from src.api.database import SessionLocal, engine
from src.api import models
import csv
import os

def seed_standard_accounts():
    db = SessionLocal()

    # 1. Seed BR GAAP from CSV
    print("Seeding BR GAAP accounts...")
    csv_path = os.path.join(os.path.dirname(__file__), 'br_gaap_standard.csv')

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Check if exists
                existing = db.query(models.StandardAccount).filter_by(
                    code=row['code'],
                    template_type='br_gaap'
                ).first()

                if not existing:
                    db_acc = models.StandardAccount(
                        code=row['code'],
                        name=row['name'],
                        type=row['type'],
                        template_type='br_gaap'
                    )
                    db.add(db_acc)
                    count += 1
            db.commit()
            print(f"Added {count} new BR GAAP accounts.")
    except FileNotFoundError:
        print(f"Warning: {csv_path} not found. Skipping BR GAAP seed.")

    # 2. Seed Condo Accounts (Hardcoded for now, or move to CSV later)
    print("Seeding Condo accounts...")
    accounts_condo = [
        # Receitas
        {"code": "1", "name": "RECEITAS", "type": "Revenue", "template": "condo"},
        {"code": "1.1", "name": "RECEITAS ORDINÁRIAS", "type": "Revenue", "template": "condo"},
        {"code": "1.1.01", "name": "Taxa de Condomínio", "type": "Revenue", "template": "condo"},
        {"code": "1.1.02", "name": "Fundo de Reserva", "type": "Revenue", "template": "condo"},
        {"code": "1.2", "name": "RECEITAS EXTRAORDINÁRIAS", "type": "Revenue", "template": "condo"},

        # Despesas
        {"code": "2", "name": "DESPESAS", "type": "Expense", "template": "condo"},
        {"code": "2.1", "name": "DESPESAS OPERACIONAIS", "type": "Expense", "template": "condo"},
        {"code": "2.1.01", "name": "Pessoal e Encargos", "type": "Expense", "template": "condo"},
        {"code": "2.1.02", "name": "Consumo (Água/Luz/Gás)", "type": "Expense", "template": "condo"},
        {"code": "2.1.03", "name": "Manutenção e Conservação", "type": "Expense", "template": "condo"},
        {"code": "2.1.04", "name": "Administrativas", "type": "Expense", "template": "condo"},
        {"code": "2.1.05", "name": "Financeiras", "type": "Expense", "template": "condo"},

        # Ativo (Simplificado para condomínio que muitas vezes é regime de caixa híbrido)
        {"code": "3", "name": "ATIVO / DISPONIBILIDADES", "type": "Asset", "template": "condo"},
        {"code": "3.1", "name": "Caixa e Bancos", "type": "Asset", "template": "condo"},
        {"code": "3.2", "name": "Inadimplência (A Receber)", "type": "Asset", "template": "condo"},
    ]

    count_condo = 0
    for acc in accounts_condo:
        existing = db.query(models.StandardAccount).filter_by(code=acc["code"], template_type=acc["template"]).first()
        if not existing:
            db_acc = models.StandardAccount(
                code=acc["code"],
                name=acc["name"],
                type=acc["type"],
                template_type=acc["template"]
            )
            db.add(db_acc)
            count_condo += 1

    db.commit()
    print(f"Added {count_condo} new Condo accounts.")
    db.close()

if __name__ == "__main__":
    # Ensure tables exist (Alembic should handle this in prod, but for local scripts/dev)
    # models.Base.metadata.create_all(bind=engine)
    seed_standard_accounts()
