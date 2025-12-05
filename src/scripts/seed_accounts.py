from sqlalchemy.orm import Session
from src.api.database import SessionLocal, engine
from src.api import models

def seed_standard_accounts():
    db = SessionLocal()

    # Re-seed logic:
    # Since we added parent_id, we might want to clear existing ones or just update them.
    # For simplicity in this dev environment, if the schema changed significantly (columns added),
    # the previous code might fail if the DB wasn't migrated.
    # But assuming we are running in a state where tables are created/updated.

    # We will try to fetch existing accounts. If none, we seed.
    if db.query(models.StandardAccount).count() > 0:
        print("Standard accounts exist. Checking if hierarchy needs update...")
        # Check if parent_id is null for accounts that look like children (e.g. 1.1)
        # If so, we might want to run an update pass.
        # But for now, let's just proceed with the definition list and upsert.
        pass

    accounts_br_gaap = [
        # Ativo
        {"code": "1", "name": "ATIVO", "type": "Asset", "template": "br_gaap", "level": 1},
        {"code": "1.1", "name": "ATIVO CIRCULANTE", "type": "Asset", "template": "br_gaap", "level": 2},
        {"code": "1.1.01", "name": "Caixa e Equivalentes de Caixa", "type": "Asset", "template": "br_gaap", "level": 3},
        {"code": "1.1.02", "name": "Contas a Receber", "type": "Asset", "template": "br_gaap", "level": 3},
        {"code": "1.1.03", "name": "Estoques", "type": "Asset", "template": "br_gaap", "level": 3},
        {"code": "1.2", "name": "ATIVO NÃO CIRCULANTE", "type": "Asset", "template": "br_gaap", "level": 2},

        # Passivo
        {"code": "2", "name": "PASSIVO", "type": "Liability", "template": "br_gaap", "level": 1},
        {"code": "2.1", "name": "PASSIVO CIRCULANTE", "type": "Liability", "template": "br_gaap", "level": 2},
        {"code": "2.1.01", "name": "Fornecedores", "type": "Liability", "template": "br_gaap", "level": 3},
        {"code": "2.1.02", "name": "Obrigações Trabalhistas", "type": "Liability", "template": "br_gaap", "level": 3},
        {"code": "2.1.03", "name": "Obrigações Tributárias", "type": "Liability", "template": "br_gaap", "level": 3},
        {"code": "2.2", "name": "PASSIVO NÃO CIRCULANTE", "type": "Liability", "template": "br_gaap", "level": 2},
        {"code": "2.3", "name": "PATRIMÔNIO LÍQUIDO", "type": "Equity", "template": "br_gaap", "level": 2},

        # Resultado
        {"code": "3", "name": "RECEITAS", "type": "Revenue", "template": "br_gaap", "level": 1},
        {"code": "4", "name": "CUSTOS E DESPESAS", "type": "Expense", "template": "br_gaap", "level": 1},
    ]

    accounts_condo = [
        # Receitas
        {"code": "100", "name": "RECEITAS ORDINÁRIAS", "type": "Revenue", "template": "condo", "level": 1},
        {"code": "101", "name": "Taxa de Condomínio", "type": "Revenue", "template": "condo", "level": 2},
        {"code": "102", "name": "Fundo de Reserva", "type": "Revenue", "template": "condo", "level": 2},
        {"code": "103", "name": "Acordos e Multas", "type": "Revenue", "template": "condo", "level": 2},

        # Despesas
        {"code": "200", "name": "DESPESAS OPERACIONAIS", "type": "Expense", "template": "condo", "level": 1},
        {"code": "201", "name": "Pessoal e Encargos", "type": "Expense", "template": "condo", "level": 2},
        {"code": "202", "name": "Consumo (Água/Luz/Gás)", "type": "Expense", "template": "condo", "level": 2},
        {"code": "203", "name": "Manutenção e Conservação", "type": "Expense", "template": "condo", "level": 2},
        {"code": "204", "name": "Administrativas", "type": "Expense", "template": "condo", "level": 2},

        # Disponibilidades
        {"code": "300", "name": "DISPONIBILIDADES (Caixa/Bancos)", "type": "Asset", "template": "condo", "level": 1},

        # Inadimplência
        {"code": "400", "name": "CONTAS A RECEBER (Inadimplência)", "type": "Asset", "template": "condo", "level": 1},
    ]

    all_accounts = accounts_br_gaap + accounts_condo

    # Helper to find parent ID
    # This assumes parents are processed before children or we do two passes.
    # The lists above are ordered, so parents come first usually.
    # But strict hierarchy: 1.1 parent is 1. 1.1.01 parent is 1.1.

    # We need to map code -> db_id to resolve parents.
    # Since we might be updating, we should read existing into a dict.

    # First pass: Create or ensure exists
    code_map = {} # (code, template) -> id

    for acc in all_accounts:
        existing = db.query(models.StandardAccount).filter_by(code=acc["code"], template_type=acc["template"]).first()
        if not existing:
            print(f"Creating {acc['code']}...")
            db_acc = models.StandardAccount(
                code=acc["code"],
                name=acc["name"],
                type=acc["type"],
                template_type=acc["template"],
                level=acc["level"],
                is_active=True
            )
            db.add(db_acc)
            db.flush() # to get ID
            code_map[(acc["code"], acc["template"])] = db_acc.id
        else:
            # Update fields if needed
            existing.level = acc["level"]
            code_map[(acc["code"], acc["template"])] = existing.id

    db.commit()

    # Second pass: Update parents
    for acc in all_accounts:
        if acc["level"] > 1:
            # Infer parent code
            # BR GAAP logic: 1.1 -> 1; 1.1.01 -> 1.1
            parent_code = None
            if "." in acc["code"]:
                parts = acc["code"].rsplit(".", 1)
                parent_code = parts[0]
            elif len(acc["code"]) > 1:
                # Condo logic: 101 -> 100? No, 100 is parent of 101?
                # The list says 100 is Level 1, 101 is Level 2.
                # If structure is not dot-based, we need explicit parent definition or heuristic.
                # For Condo, let's assume 101 -> 100, 201 -> 200.
                try:
                    val = int(acc["code"])
                    parent_val = (val // 100) * 100
                    if parent_val != val:
                         parent_code = str(parent_val)
                except:
                    pass

            if parent_code:
                parent_id = code_map.get((parent_code, acc["template"]))
                current_id = code_map.get((acc["code"], acc["template"]))

                if parent_id and current_id:
                     db.query(models.StandardAccount).filter(models.StandardAccount.id == current_id).update({"parent_id": parent_id})

    db.commit()
    print("Standard accounts seeded and hierarchy updated.")
    db.close()

if __name__ == "__main__":
    # Create tables if not exist
    models.Base.metadata.create_all(bind=engine)
    seed_standard_accounts()
