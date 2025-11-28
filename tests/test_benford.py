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

if __name__ == '__main__':
    unittest.main()
