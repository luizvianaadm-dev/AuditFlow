import unittest
from src.scripts.duplicate_analysis import find_duplicates

class TestDuplicateAnalysis(unittest.TestCase):

    def test_exact_duplicates(self):
        """Test case where vendor and amount are exactly the same."""
        transactions = [
            {"id": 1, "vendor": "Fornecedor A", "amount": 100.0},
            {"id": 2, "vendor": "Fornecedor A", "amount": 100.0}
        ]
        result = find_duplicates(transactions)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["similarity_score"], 100)
        self.assertEqual(len(result[0]["transactions"]), 2)

    def test_fuzzy_duplicates(self):
        """Test case: 'Fornecedor Alpha' vs 'Fornecedor Alpha S.A.' (same amount)."""
        transactions = [
            {"id": 1, "vendor": "Fornecedor Alpha", "amount": 500.0},
            {"id": 2, "vendor": "Fornecedor Alpha S.A.", "amount": 500.0},
            {"id": 3, "vendor": "Outro Fornecedor", "amount": 500.0}
        ]
        # "Fornecedor Alpha" vs "Fornecedor Alpha S.A." has token_sort_ratio ~89 > 85

        result = find_duplicates(transactions)

        # We expect 1 pair found (1 vs 2)
        self.assertEqual(len(result), 1)
        tx_ids = [tx["id"] for tx in result[0]["transactions"]]
        self.assertIn(1, tx_ids)
        self.assertIn(2, tx_ids)
        self.assertNotIn(3, tx_ids)
        self.assertGreater(result[0]["similarity_score"], 85)

    def test_negative_case_different_vendors(self):
        """Test case: Different vendors, same amount."""
        transactions = [
            {"id": 1, "vendor": "Apple Inc", "amount": 1000.0},
            {"id": 2, "vendor": "Google LLC", "amount": 1000.0}
        ]
        result = find_duplicates(transactions)
        self.assertEqual(len(result), 0)

    def test_negative_case_different_amounts(self):
        """Test case: Similar vendors, different amounts."""
        transactions = [
            {"id": 1, "vendor": "Fornecedor A", "amount": 100.0},
            {"id": 2, "vendor": "Fornecedor A", "amount": 101.0}
        ]
        result = find_duplicates(transactions)
        self.assertEqual(len(result), 0)

    def test_empty_input(self):
        self.assertEqual(find_duplicates([]), [])

if __name__ == '__main__':
    unittest.main()
