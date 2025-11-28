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
    }
