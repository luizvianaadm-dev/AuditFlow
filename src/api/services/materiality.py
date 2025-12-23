from typing import Dict, Any, Optional

class MaterialityEngine:
    """
    Core Logic for NBC TA 320 - Materiality in Planning and Performing an Audit.
    Supports 'Empresarial' and 'Condominial' strategies.
    [Master Logic: Phase 2 - Planejamento Estratégico]
    """

    BENCHMARKS_EMP = {
        "gross_revenue": {"range": (0.005, 0.01), "label": "0.5% a 1% da Receita Bruta"}, # 0.5% - 1%
        "total_assets": {"range": (0.01, 0.02), "label": "1% a 2% do Ativo Total"},    # 1% - 2%
        "net_profit":   {"range": (0.05, 0.10), "label": "5% a 10% do Lucro Líquido"},  # 5% - 10%
        "equity":       {"range": (0.01, 0.05), "label": "1% a 5% do Patrimônio Líquido"} # 1% - 5%
    }

    BENCHMARKS_CONDO = {
        "total_expenses": {"range": (0.01, 0.03), "label": "1% a 3% das Despesas Totais"}, # 1% - 3%
        "gross_revenue":  {"range": (0.005, 0.01), "label": "0.5% a 1% da Arrecadação Total"}
    }

    def calculate_pm(self, base_value: float, percentage: float) -> float:
        """Calculates Overall Materiality (Planejamento - PM)"""
        return base_value * percentage

    def calculate_te(self, pm: float, risk_factor: str = "normal") -> float:
        """
        Calculates Performance Materiality (Execução - TE).
        Usually 60-85% of PM based on risk.
        """
        ranges = {
            "high": 0.60,
            "normal": 0.75,
            "low": 0.85
        }
        factor = ranges.get(risk_factor, 0.75)
        return pm * factor

    def calculate_ctt(self, pm: float) -> float:
        """
        Calculates Clearly Trivial Threshold (CTT / Limite de Trivialidade).
        Usually 5% of PM.
        """
        return pm * 0.05

    def suggest_benchmark(self, entity_type: str, financial_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyzes financial data and suggests the most appropriate benchmark.
        """
        if entity_type == "Condominio":
            # Prefer Expenses
            if "total_expenses" in financial_data:
                return {"benchmark": "total_expenses", "base_value": financial_data["total_expenses"], "recommended_pct": 0.02}
            elif "gross_revenue" in financial_data:
                return {"benchmark": "gross_revenue", "base_value": financial_data["gross_revenue"], "recommended_pct": 0.01}
        else:
            # Empresarial logic (simplified)
            # 1. Profit oriented? -> Profit
            if financial_data.get("net_profit", 0) > 0:
                 return {"benchmark": "net_profit", "base_value": financial_data["net_profit"], "recommended_pct": 0.05}
            # 2. Loss maker? -> Revenue or Assets
            if financial_data.get("gross_revenue", 0) > 0:
                return {"benchmark": "gross_revenue", "base_value": financial_data["gross_revenue"], "recommended_pct": 0.005}
            
        return {"benchmark": "manual", "base_value": 0.0, "recommended_pct": 0.0}

materiality_engine = MaterialityEngine()
