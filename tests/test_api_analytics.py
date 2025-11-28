from fastapi.testclient import TestClient
from src.api.main import app
import unittest

client = TestClient(app)

class TestApiAnalytics(unittest.TestCase):

    def test_benford_endpoint_valid(self):
        """
        Test /analyze/benford with valid data.
        """
        payload = {
            "transactions": [100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0]
        }
        response = client.post("/analyze/benford", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("expected", data)
        self.assertIn("observed", data)
        self.assertIn("anomalies", data)

        # Verify observed frequencies (basic check)
        # We sent one of each digit 1-9, so frequencies should be uniform ~0.11
        # But wait, logic extracts first digit.
        # 100 -> 1, 200 -> 2...
        # So yes, 1 of each.
        self.assertAlmostEqual(data["observed"]["1"], 1/9, delta=0.01)

    def test_benford_endpoint_empty(self):
        """
        Test /analyze/benford with empty list.
        """
        payload = {
            "transactions": []
        }
        response = client.post("/analyze/benford", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Transaction list cannot be empty")

    def test_benford_endpoint_invalid_json(self):
        """
        Test /analyze/benford with invalid input types.
        """
        payload = {
            "transactions": ["invalid", "numbers"]
        }
        response = client.post("/analyze/benford", json=payload)
        # Pydantic validation error is usually 422
        self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main()
