import unittest
import math
from src.scripts.benford_analysis import calculate_benford

class TestBenfordAnalysis(unittest.TestCase):

    def test_benford_perfect_dataset(self):
        """
        Test 1: "Perfect" dataset (approximately follows Benford's Law).
        We generate a dataset that matches the expected probabilities.
        """
        # Benford probabilities for digits 1-9
        # 1: 30.1%, 2: 17.6%, 3: 12.5%, 4: 9.7%, 5: 7.9%, 6: 6.7%, 7: 5.8%, 8: 5.1%, 9: 4.6%

        # Construct a dataset of 1000 items following these ratios exactly (as close as possible with integers)
        data = []
        distribution = {
            1: 301, 2: 176, 3: 125, 4: 97, 5: 79, 6: 67, 7: 58, 8: 51, 9: 46
        }

        for digit, count in distribution.items():
            # Create values starting with 'digit'
            # e.g., for digit 1, values can be 10, 100, 15, etc.
            # Using simple values like digit * 10
            data.extend([float(digit * 10)] * count)

        result = calculate_benford(data)

        # Expecting no anomalies since we matched the distribution closely
        # However, due to rounding and small deviations (sum of probs is 1.0), let's check.
        # 301/1000 = 0.301. Expected log10(2) approx 0.30103. Deviation < 0.05.

        self.assertEqual(len(result["anomalies"]), 0, f"Expected no anomalies for perfect dataset, found: {result['anomalies']}")
        self.assertEqual(result["sample_size"], 1000)

        # Check digit 1 specifically
        expected_1 = math.log10(1 + 1/1) # ~0.301
        observed_1 = result["observed_frequencies"][1]
        self.assertAlmostEqual(observed_1, 0.301, delta=0.001)

    def test_benford_biased_dataset(self):
        """
        Test 2: "Biased" dataset (manufactured anomalies).
        Forces a high frequency of digit 9, which should be rare (4.6%).
        """
        # 100 values, 90 of them start with 9.
        # Observed digit 9 = 0.90. Expected = 0.046. Deviation ~ 0.85 > 0.05.
        data = [900.0] * 90 + [100.0] * 10

        result = calculate_benford(data)

        self.assertIn(9, result["anomalies"], "Digit 9 should be flagged as an anomaly")

        # Check digit 9 details
        details_9 = next(item for item in result["details"] if item["digit"] == 9)
        self.assertTrue(details_9["is_anomaly"])
        self.assertGreater(details_9["deviation"], 0.05)

    def test_empty_or_invalid_input(self):
        """Test empty list and zeros handling"""
        self.assertEqual(calculate_benford([]), {
            "expected_frequencies": {},
            "observed_frequencies": {},
            "anomalies": [],
            "details": [],
            "sample_size": 0
        })

        # Zeros should be ignored (no first digit 1-9)
        res = calculate_benford([0.0, 0.0])
        self.assertEqual(res["sample_size"], 0)

if __name__ == '__main__':
    unittest.main()
