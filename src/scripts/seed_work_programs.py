from sqlalchemy.orm import Session
from src.api.database import SessionLocal, engine
from src.api import models

def seed_audit_programs():
    db = SessionLocal()

    if db.query(models.AuditArea).first():
        print("Audit Programs already seeded.")
        db.close()
        return

    # Areas for BR GAAP
    areas = [
        {
            "name": "Disponibilidades (Caixa e Equivalentes)",
            "template": "br_gaap",
            "procedures": [
                "Obter o Balancete e Razão das contas de caixa e bancos.",
                "Realizar circularização de 100% dos saldos bancários relevantes.",
                "Conciliar as respostas de circularização com o razão contábil.",
                "Testar a conversão de saldos em moeda estrangeira (se houver)."
            ]
        },
        {
            "name": "Clientes (Contas a Receber)",
            "template": "br_gaap",
            "procedures": [
                "Obter relatório de envelhecimento (aging list) e conciliar com o razão.",
                "Circularizar uma amostra de clientes (Positiva/Em Branco).",
                "Realizar teste de recebimento subsequente (vide liquidação após fechamento).",
                "Recalcular a PCLD (Provisão para Crédito de Liquidação Duvidosa)."
            ]
        },
        {
            "name": "Estoques",
            "template": "br_gaap",
            "procedures": [
                "Acompanhar a contagem física de estoques (Inventário).",
                "Testar o custo (Custo Médio ou PEPS) vs Valor Realizável Líquido.",
                "Verificar corte (Cut-off) de entradas e saídas no fechamento."
            ]
        },
        {
            "name": "Ativo Imobilizado",
            "template": "br_gaap",
            "procedures": [
                "Obter mapa de movimentação do imobilizado.",
                "Testar adições relevantes (nf de compra) e baixas.",
                "Recalcular a depreciação do exercício.",
                "Avaliar necessidade de teste de impairment."
            ]
        },
        {
            "name": "Passivo Circulante (Fornecedores/Obrigações)",
            "template": "br_gaap",
            "procedures": [
                "Obter listagem de fornecedores em aberto.",
                "Circularizar principais fornecedores.",
                "Realizar busca de passivos não registrados (Search for Unrecorded Liabilities).",
                "Recalcular provisões de férias e 13º salário (Folha)."
            ]
        },
        {
            "name": "Receitas",
            "template": "br_gaap",
            "procedures": [
                "Realizar análise analítica substantiva (comparativo mensal).",
                "Testar corte (Cut-off) de vendas.",
                "Selecionar amostra de notas fiscais e rastrear até o recebimento."
            ]
        }
    ]

    for area_data in areas:
        area = models.AuditArea(name=area_data["name"], template_type=area_data["template"])
        db.add(area)
        db.flush() # get ID

        for proc_desc in area_data["procedures"]:
            proc = models.AuditProcedure(area_id=area.id, description=proc_desc)
            db.add(proc)

    db.commit()
    print("Audit Programs seeded successfully.")
    db.close()

if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    seed_audit_programs()
