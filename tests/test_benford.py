import unittest
import math
import random
from src.scripts.benford_analysis import calculate_benford

class TestBenfordAnalysis(unittest.TestCase):

    def test_perfect_benford(self):
        """
        Test with a dataset that closely follows Benford's Law.
        We generate a large dataset based on the probability distribution.
        """
        # Generate data that follows Benford's law
        # P(d) = log10(1 + 1/d)
        # We can simulate this by generating numbers 10^x where x is uniform in [a, b]
        # Because if X is uniform in [A, B], then Y = 10^X follows Benford's law approximately
        # for large ranges.
        # Alternatively, we can just construct a list with exact counts.

        data = []
        total_items = 1000
        expected_distribution = {d: math.log10(1 + 1/d) for d in range(1, 10)}

        for digit, prob in expected_distribution.items():
            count = int(prob * total_items)
            # Create numbers starting with 'digit'
            # e.g., if digit is 1, we add 1, 10, 100, 15, 1.2, etc.
            # To be simple, we just add the digit itself 'count' times.
            # But the function extracts the first digit, so 1, 10, 199 all count as 1.
            data.extend([float(digit)] * count)

        # Add a few more to round up to total items if int truncation missed some,
        # but for this test, we just want to be within the 5% tolerance.

        result = calculate_benford(data)

        # We expect 0 anomalies because we constructed it to match frequencies
        # However, due to integer truncation, there might be slight deviations,
        # but 1000 items should be precise enough for < 5% error.

        # Let's verify specific observed values match roughly expected
        for d in range(1, 10):
            obs = result['observed'][d]
            exp = result['expected'][d]
            self.assertAlmostEqual(obs, exp, delta=0.05, msg=f"Digit {d} observed {obs} vs expected {exp}")

        self.assertEqual(len(result['anomalies']), 0, f"Expected 0 anomalies, got {result['anomalies']}")

    def test_biased_data(self):
        """
        Test with data heavily biased towards starting with 9.
        """
        # 100 items, 90 starting with 9, 10 starting with 1.
        data = [9.0] * 90 + [1.0] * 10

        result = calculate_benford(data)

        # Expected for 9 is log10(1 + 1/9) ~= 0.045
        # Observed for 9 is 0.90
        # Diff is ~0.85, which is > 0.05. So 9 should be an anomaly.

        # Expected for 1 is log10(2) ~= 0.301
        # Observed for 1 is 0.10
        # Diff is ~0.20, which is > 0.05. So 1 should be an anomaly.

        self.assertIn(9, result['anomalies'])
        self.assertIn(1, result['anomalies'])

    def test_edge_cases(self):
        """
        Test empty list, zeros, negatives.
        """
        data = [0, 0.0, -50.0, -120.0] # Should effectively be [5, 1]
        result = calculate_benford(data)

        # Total valid items = 2 (50, 120) -> first digits 5 and 1.
        # Frequencies: 1: 0.5, 5: 0.5, others 0.

        # Expected 1: 0.301. Obs: 0.5. Diff: 0.2 (Anomaly)
        # Expected 5: 0.079. Obs: 0.5. Diff: 0.42 (Anomaly)

        self.assertEqual(result['observed'][1], 0.5)
        self.assertEqual(result['observed'][5], 0.5)
        self.assertEqual(result['observed'][2], 0.0)
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
