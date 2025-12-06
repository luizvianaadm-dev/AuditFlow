import unittest
import pandas as pd
from src.scripts.reconciliation_engine import ReconciliationEngine
from datetime import datetime

class TestReconciliationEngine(unittest.TestCase):
    def test_process_reconciliation_exact_match(self):
        # Create Dummy Data
        # Bank: 100.00 on 2023-10-01
        bank_data = {
            "Data": ["01/10/2023"],
            "Valor": ["100,00"],
            "Codigo Conciliação": ["CONF123"]
        }
        bank_df = pd.DataFrame(bank_data)

        # Financial: 30, 30, 40 on 2023-10-01
        fin_data = {
            "Data movimento": ["01/10/2023", "01/10/2023", "01/10/2023", "02/10/2023"],
            "Valor (R$)": ["30,00", "30,00", "40,00", "50,00"],
            "Historico": ["Payment A", "Payment B", "Payment C", "Other"]
        }
        fin_df = pd.DataFrame(fin_data)

        results = ReconciliationEngine.process_reconciliation(bank_df, fin_df)

        self.assertEqual(len(results), 1)
        match = results[0]

        self.assertTrue(match["match_found"])
        self.assertEqual(match["bank_entry"]["code"], "CONF123")
        self.assertEqual(len(match["financial_ids"]), 3)

        # Verify amounts
        amounts = [f["amount"] for f in match["financial_matches"]]
        self.assertEqual(sum(amounts), 100.0)
        self.assertIn(30.0, amounts)
        self.assertIn(40.0, amounts)

    def test_process_reconciliation_no_match(self):
        # Bank: 200.00
        # Fin: 30, 30, 40 (Sum 100)
        bank_data = {
            "Data": ["01/10/2023"],
            "Valor": ["200,00"],
            "Codigo Conciliação": ["CONF999"]
        }
        bank_df = pd.DataFrame(bank_data)

        fin_data = {
            "Data movimento": ["01/10/2023", "01/10/2023", "01/10/2023"],
            "Valor (R$)": ["30,00", "30,00", "40,00"],
        }
        fin_df = pd.DataFrame(fin_data)

        results = ReconciliationEngine.process_reconciliation(bank_df, fin_df)
        self.assertFalse(results[0]["match_found"])

if __name__ == "__main__":
    unittest.main()
