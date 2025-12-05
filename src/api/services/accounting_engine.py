from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class CashFlowResult(BaseModel):
    operating_flow: float
    investing_flow: float
    financing_flow: float
    net_increase: float
    reconciliation: Dict[str, float] # e.g. {"start_cash": 100, "end_cash": 150, "check": True}
    details: Dict[str, Any] # Detailed breakdown

class DMPLResult(BaseModel):
    matrix: List[Dict[str, Any]] # Rows
    validation: Dict[str, Any] # { "dre_match": True, "diff": 0.0 }

def calculate_cash_flow(
    net_income: float,
    depreciation_amortization: float,
    working_capital_changes: Dict[str, float],
    investing_activities: List[Dict[str, Any]],
    financing_activities: List[Dict[str, Any]],
    initial_cash_balance: float = 0.0
) -> CashFlowResult:
    """
    Calculates Indirect Cash Flow (DFC).

    working_capital_changes: {
        "accounts_receivable": -500 (Increase in Asset = Cash Outflow),
        "inventory": 200 (Decrease in Asset = Cash Inflow),
        "accounts_payable": 100 (Increase in Liab = Cash Inflow)
    }
    """

    # 1. Operating Activities
    # Start with Net Income
    operating_flow = net_income

    # Add back non-cash items (Depreciation)
    operating_flow += depreciation_amortization

    # Adjust for Working Capital
    wc_total = sum(working_capital_changes.values())
    operating_flow += wc_total

    operating_breakdown = {
        "net_income": net_income,
        "depreciation": depreciation_amortization,
        "working_capital": working_capital_changes,
        "total": operating_flow
    }

    # 2. Investing Activities
    # Items like [{"description": "Capex", "value": -1000}]
    investing_flow = sum(item["value"] for item in investing_activities)

    # 3. Financing Activities
    financing_flow = sum(item["value"] for item in financing_activities)

    # Net Increase
    net_increase = operating_flow + investing_flow + financing_flow

    final_cash = initial_cash_balance + net_increase

    return CashFlowResult(
        operating_flow=operating_flow,
        investing_flow=investing_flow,
        financing_flow=financing_flow,
        net_increase=net_increase,
        reconciliation={
            "initial_cash": initial_cash_balance,
            "final_cash_calculated": final_cash,
            "net_change": net_increase
        },
        details={
            "operating": operating_breakdown,
            "investing": investing_activities,
            "financing": financing_activities
        }
    )

def calculate_dmpl(
    opening_balances: Dict[str, float],
    net_income: float,
    capital_changes: float, # Increase/Decrease in Capital
    reserves_allocation: Dict[str, float], # { "legal": 500, "statutory": 200 } -> deducted from Retained Earnings, added to Reserves
    dividends_distributed: float, # Negative value usually
    other_comprehensive_income: float = 0.0 # AAP
) -> DMPLResult:
    """
    Calculates DMPL (Demonstração das Mutações do Patrimônio Líquido).
    Columns: Capital Social, Reservas de Capital, Reservas de Lucros, Lucros/Prej Acumulados, Outros, Total.
    """

    # Standard Columns
    cols = ["capital_social", "reservas_capital", "reservas_lucros", "lucros_acumulados", "outros_res", "total"]

    # 1. Opening Balance Row
    row_opening = {c: opening_balances.get(c, 0.0) for c in cols if c != "total"}
    row_opening["total"] = sum(row_opening.values())
    row_opening["description"] = "Saldo Inicial"

    # 2. Capital Increase Row
    row_capital = {c: 0.0 for c in cols}
    row_capital["capital_social"] = capital_changes
    row_capital["total"] = capital_changes
    row_capital["description"] = "Aumento/Redução de Capital"

    # 3. Net Income Row
    row_income = {c: 0.0 for c in cols}
    row_income["lucros_acumulados"] = net_income
    row_income["total"] = net_income
    row_income["description"] = "Lucro Líquido do Exercício"

    # 4. Allocations Row (Internal Transfers)
    # Transfer from Lucros Acumulados to Reserves
    row_alloc = {c: 0.0 for c in cols}
    total_alloc = sum(reserves_allocation.values())

    # Assuming allocations go to "reservas_lucros" generically, or specific logic if we split reserves
    # For MVP, we sum all allocations to 'reservas_lucros'
    row_alloc["reservas_lucros"] = total_alloc
    row_alloc["lucros_acumulados"] = -total_alloc
    row_alloc["total"] = 0.0 # Internal movement affects columns but not Total PL (usually)
    row_alloc["description"] = "Constituição de Reservas"

    # 5. Dividends Row
    row_div = {c: 0.0 for c in cols}
    row_div["lucros_acumulados"] = dividends_distributed # Expected to be negative
    row_div["total"] = dividends_distributed
    row_div["description"] = "Dividendos Distribuídos"

    # 6. Other Comprehensive Income
    row_oci = {c: 0.0 for c in cols}
    row_oci["outros_res"] = other_comprehensive_income
    row_oci["total"] = other_comprehensive_income
    row_oci["description"] = "Outros Resultados Abrangentes"

    # 7. Closing Balance
    rows = [row_opening, row_capital, row_income, row_alloc, row_div, row_oci]

    row_closing = {c: 0.0 for c in cols}
    row_closing["description"] = "Saldo Final"

    for c in cols:
        if c == "description": continue
        row_closing[c] = sum(r.get(c, 0.0) for r in rows)

    matrix = rows + [row_closing]

    # Validation
    # Check: Delta Lucros Acumulados + Dividends + Allocations == Net Income ?
    # Or simply: Did we input Net Income correctly?
    # The requirement is: "Validate: DRE Lucro = DMPL Lucro Acumulado variation"
    # Actually, DRE Profit is the INPUT `net_income`.
    # DMPL Variation of "Lucros Acumulados" column = Final - Initial.
    # Delta = Net Income - Allocations - Dividends.
    # So Net Income = Delta + Allocations + Dividends.

    delta_lucros = row_closing["lucros_acumulados"] - row_opening["lucros_acumulados"]
    reconciled_income = delta_lucros + total_alloc - dividends_distributed # Dividends is negative, so minus negative = plus

    # Note: Dividends is negative in row. So Delta = Income - Alloc - Abs(Div).
    # Reconciled = Delta + Alloc + Abs(Div)
    # If `dividends_distributed` is passed as negative number (e.g. -1000):
    # Delta = Income - Alloc + Div
    # Income = Delta + Alloc - Div

    check_diff = abs(reconciled_income - net_income)

    return DMPLResult(
        matrix=matrix,
        validation={
            "dre_net_income": net_income,
            "dmpl_implied_income": reconciled_income,
            "match": check_diff < 0.01,
            "diff": check_diff
        }
    )
