from typing import List, Dict, Any, Optional
from thefuzz import fuzz

def find_duplicates(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identifies potential duplicate transactions based on exact amount match
    and fuzzy vendor name matching.

    Args:
        transactions: List of dictionaries with keys 'amount' (float) and 'vendor' (str).
                      Optional 'id' key for identification.

    Returns:
        List of groups (dictionaries) containing potential duplicates.
    """
    if not transactions:
        return []

    # 1. Group by exact amount
    grouped_by_amount: Dict[float, List[Dict[str, Any]]] = {}

    for tx in transactions:
        amount = tx.get('amount')
        if amount is None:
            continue

        if amount not in grouped_by_amount:
            grouped_by_amount[amount] = []
        grouped_by_amount[amount].append(tx)

    suspect_groups = []

    # 2. Analyze each group for vendor similarity
    for amount, group in grouped_by_amount.items():
        if len(group) < 2:
            continue

        # Compare every pair in the group
        # To avoid duplicate pairs and self-comparison, use nested loop
        # We need to cluster them. A simple pair-wise approach is requested: "marque o par".
        # But we might have A, B, C where A~B and B~C.
        # Let's stick to finding pairs or small groups.
        # The requirement says "marque o par".

        # We will iterate and find pairs that satisfy the condition.
        # To avoid outputting the same pair twice (A, B) and (B, A), we use indices.

        checked_pairs = set()

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                tx1 = group[i]
                tx2 = group[j]

                vendor1 = str(tx1.get('vendor', '')).lower()
                vendor2 = str(tx2.get('vendor', '')).lower()

                # Use token_sort_ratio as requested
                similarity = fuzz.token_sort_ratio(vendor1, vendor2)

                if similarity > 85:
                    suspect_groups.append({
                        "amount": amount,
                        "similarity_score": similarity,
                        "transactions": [tx1, tx2]
                    })

    return suspect_groups
