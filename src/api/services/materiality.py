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
        "total_expenses": {"range": (0.01, 0.03), "label": "1% a 3% das Despesas Totais"}, 
        "gross_revenue":  {"range": (0.005, 0.01), "label": "0.5% a 1% da Arrecadação Total"}
    }

    RISK_FACTORS = [
        {"id": "new_client", "label": "Primeira Auditoria (Cliente Novo)", "weight": 2},
        {"id": "control_failures", "label": "Falhas Relevantes de Controle Interno", "weight": 2},
        {"id": "history_errors", "label": "Histórico de Ajustes/Erros", "weight": 1},
        {"id": "volatile_env", "label": "Ambiente Econômico Volátil / Mudanças", "weight": 1},
        {"id": "public_interest", "label": "Entidade de Interesse Público", "weight": 1},
        {"id": "fraud_risk", "label": "Indicadores de Risco de Fraude", "weight": 3}
    ]

    def calculate_risk_score(self, risks_present: list) -> int:
        """Sum weights of checked risks."""
        score = 0
        for r in self.RISK_FACTORS:
            if r["id"] in risks_present:
                score += r["weight"]
        return score

    def get_recommended_percentage(self, benchmark_range: tuple, risk_score: int) -> float:
        """
        Adjusts percentage based on Risk Score.
        Higher Risk (Score > 0) -> Lower % (More conservative).
        Lower Risk (Score 0) -> Higher % (Less conservative).
        
        Logic:
        - Score 0-1 (Low Risk): Max %
        - Score 2-4 (Medium Risk): Avg %
        - Score 5+ (High Risk): Min %
        """
        min_pct, max_pct = benchmark_range
        
        if risk_score <= 1:
            return max_pct
        elif risk_score <= 4:
            return (min_pct + max_pct) / 2
        else:
            return min_pct

    def calculate_pm(self, base_value: float, percentage: float) -> float:
        """Calculates Overall Materiality (Planejamento - PM)"""
        return base_value * percentage

    def calculate_te(self, pm: float, risk_score: int = 0) -> float:
        """
        Calculates Performance Materiality (Execução - TE).
        Usually 60-85% of PM based on risk.
        Low Risk -> 85%
        Med Risk -> 75%
        High Risk -> 60%
        """
        if risk_score <= 1: return pm * 0.85
        if risk_score <= 4: return pm * 0.75
        return pm * 0.60

    def calculate_ctt(self, pm: float) -> float:
        """
        Calculates Clearly Trivial Threshold (CTT / Limite de Trivialidade).
        Usually 5% of PM.
        """
        # AMPT / CTT logic
        return pm * 0.05
    
    def calculate_adjusted_materiality(self, calculated_value: float) -> float:
        """
        Rounds the materiality to a clean number (e.g. nearest 100/1000).
        """
        # Simple rounding logic
        if calculated_value < 1000: return round(calculated_value, -1)
        if calculated_value < 10000: return round(calculated_value, -2)
        if calculated_value < 100000: return round(calculated_value, -3)
        return round(calculated_value, -3) # Round to thousand

    def suggest_benchmark(self, entity_type: str, financial_data: Dict[str, float], risks_present: list = []) -> Dict[str, Any]:
        """
        Analyzes financial data and suggests the most appropriate benchmark.
        """
        risk_score = self.calculate_risk_score(risks_present)
        
        chosen = {"benchmark": "manual", "base_value": 0.0, "range": (0.0, 0.0), "recommended_pct": 0.0}

        if entity_type == "Condominio":
            # Prefer Expenses
            if "total_expenses" in financial_data:
                chosen = {
                    "benchmark": "total_expenses", 
                    "base_value": financial_data["total_expenses"], 
                    "range": self.BENCHMARKS_CONDO["total_expenses"]["range"],
                    "label": self.BENCHMARKS_CONDO["total_expenses"]["label"]
                }
            elif "gross_revenue" in financial_data:
                 chosen = {
                    "benchmark": "gross_revenue", 
                    "base_value": financial_data["gross_revenue"], 
                    "range": self.BENCHMARKS_CONDO["gross_revenue"]["range"],
                    "label": self.BENCHMARKS_CONDO["gross_revenue"]["label"]
                }
        else:
            # Empresarial logic
            # 1. Profit oriented? -> Profit
            if financial_data.get("net_profit", 0) > 0:
                 chosen = {
                    "benchmark": "net_profit", 
                    "base_value": financial_data["net_profit"], 
                    "range": self.BENCHMARKS_EMP["net_profit"]["range"],
                    "label": self.BENCHMARKS_EMP["net_profit"]["label"]
                }
            # 2. Loss maker? -> Revenue or Assets
            elif financial_data.get("gross_revenue", 0) > 0:
                chosen = {
                    "benchmark": "gross_revenue", 
                    "base_value": financial_data["gross_revenue"], 
                    "range": self.BENCHMARKS_EMP["gross_revenue"]["range"],
                    "label": self.BENCHMARKS_EMP["gross_revenue"]["label"]
                }
            elif financial_data.get("total_assets", 0) > 0:
                 chosen = {
                    "benchmark": "total_assets", 
                    "base_value": financial_data["total_assets"], 
                    "range": self.BENCHMARKS_EMP["total_assets"]["range"],
                    "label": self.BENCHMARKS_EMP["total_assets"]["label"]
                }
        
        # Calculate Percentage
        if chosen["benchmark"] != "manual":
            chosen["recommended_pct"] = self.get_recommended_percentage(chosen["range"], risk_score)
            chosen["risk_score"] = risk_score
            
        return chosen

materiality_engine = MaterialityEngine()
