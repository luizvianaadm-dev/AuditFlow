import math

def calculate_benford(values: list[float]) -> dict[str, dict[int, float] | list[int]]:
    """
    Calculates Benford's Law statistics for a list of monetary values.

    Args:
        values: A list of float values representing monetary amounts.

    Returns:
        A dictionary containing:
        - 'expected': Dictionary of expected frequencies (key: digit 1-9, value: probability).
        - 'observed': Dictionary of observed frequencies (key: digit 1-9, value: probability).
        - 'anomalies': List of digits where the absolute difference between observed and expected
                       frequency is greater than 5% (0.05).
    """

    # 1. Calculate Expected Frequencies
    expected: dict[int, float] = {d: math.log10(1 + 1/d) for d in range(1, 10)}

    # 2. Process Values to Extract First Digits
    first_digits: list[int] = []
    for v in values:
        if v == 0:
            continue
        try:
            # Handle negatives by taking abs, and handle floats strictly
            val_abs = abs(v)
            if val_abs == 0:
                continue

            # Convert to string to easily get first digit, handling scientific notation if needed
            # Or use math: first_digit = int(str(val_abs).replace('.', '').lstrip('0')[0])
            # A more robust math way:
            # 10 ** (int(math.log10(val_abs))) -> magnitude
            # val_abs // magnitude -> first digit
            # But string manipulation is often safer for edge cases in simple scripts unless performance is critical

            s = str(val_abs)
            # Remove decimal point
            s = s.replace('.', '')
            # Strip leading zeros (for numbers < 1)
            s = s.lstrip('0')

            if not s:
                continue

            digit = int(s[0])
            if 1 <= digit <= 9:
                first_digits.append(digit)

        except (ValueError, IndexError):
            continue

    total_count = len(first_digits)

    # 3. Calculate Observed Frequencies
    observed: dict[int, float] = {d: 0.0 for d in range(1, 10)}
    if total_count > 0:
        for d in first_digits:
            observed[d] += 1

        for d in observed:
            observed[d] /= total_count

    # 4. Detect Anomalies
    anomalies: list[int] = []
    for d in range(1, 10):
        diff = abs(observed[d] - expected[d])
        if diff > 0.05:
            anomalies.append(d)

    return {
        "expected": expected,
        "observed": observed,
        "anomalies": anomalies
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
