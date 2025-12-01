import math
from typing import List, Dict, Union, Any

def calculate_benford(values: List[float]) -> Dict[str, Any]:
    """
    Calculates the First Digit Law (Benford's Law) analysis for a list of monetary values.

    Args:
        values: A list of float numbers representing monetary values.

    Returns:
        A dictionary containing:
        - expected_frequencies: Dict[int, float] (1-9)
        - observed_frequencies: Dict[int, float] (1-9)
        - anomalies: List[int] (digits with deviation > 0.05)
        - details: List[Dict] with per-digit analysis
    """
    if not values:
        return {
            "expected_frequencies": {},
            "observed_frequencies": {},
            "anomalies": [],
            "details": [],
            "sample_size": 0
        }

    first_digits = []
    for v in values:
        try:
            # Handle negative numbers and zero
            abs_v = abs(v)
            if abs_v == 0:
                continue

            # Convert to string to easily get the first digit
            # Using scientific notation to handle small float issues
            s = "{:.15e}".format(abs_v)
            first_digit = int(s[0])
            if 1 <= first_digit <= 9:
                first_digits.append(first_digit)
        except ValueError:
            continue

    total_count = len(first_digits)
    if total_count == 0:
        return {
            "expected_frequencies": {},
            "observed_frequencies": {},
            "anomalies": [],
            "details": [],
            "sample_size": 0
        }

    expected_frequencies = {}
    observed_frequencies = {}
    anomalies = []
    details = []

    counts = {d: 0 for d in range(1, 10)}
    for d in first_digits:
        counts[d] += 1

    for d in range(1, 10):
        # Benford's Law: P(d) = log10(1 + 1/d)
        expected_prob = math.log10(1 + 1/d)
        observed_prob = counts[d] / total_count

        expected_frequencies[d] = round(expected_prob, 4)
        observed_frequencies[d] = round(observed_prob, 4)

        deviation = abs(observed_prob - expected_prob)
        is_anomaly = deviation > 0.05

        if is_anomaly:
            anomalies.append(d)

        details.append({
            "digit": d,
            "expected": round(expected_prob, 4),
            "observed": round(observed_prob, 4),
            "deviation": round(deviation, 4),
            "is_anomaly": is_anomaly
        })

    return {
        "expected_frequencies": expected_frequencies,
        "observed_frequencies": observed_frequencies,
        "anomalies": anomalies,
        "details": details,
        "sample_size": total_count
    }
