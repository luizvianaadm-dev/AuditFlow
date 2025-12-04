from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from thefuzz import fuzz
from collections import defaultdict

def find_duplicates(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identifies potential duplicate payments based on amount and vendor name similarity.

    Args:
        transactions: A list of dictionaries, each containing:
            - 'id': str or int (optional)
            - 'amount': float
            - 'vendor': str
            - 'date': str (ISO 8601, optional)

    Returns:
        A list of "groups" of suspicious transactions.
        Each group contains:
            - 'group_id': int
            - 'reason': str (description of why it was flagged)
            - 'transactions': List[Dict] (the transactions involved)
    """

    # 1. Group by Amount
    by_amount: Dict[float, List[Dict[str, Any]]] = defaultdict(list)
    for t in transactions:
        try:
            amt = float(t.get('amount', 0))
            if amt != 0:
                by_amount[amt].append(t)
        except (ValueError, TypeError):
            continue

    suspicious_groups: List[Dict[str, Any]] = []
    group_counter = 1

    # 2. Analyze within amount groups
    for amount, tx_list in by_amount.items():
        if len(tx_list) < 2:
            continue

        # Iterate pairs to find similar vendors
        # To avoid N^2 complexity on large sets, we could limit, but usually duplicate sets are small per amount.

        # We need to cluster them.
        # Simple approach: Check every pair. If match, add to a set of matched IDs.
        # Better approach: Build connected components?
        # Let's stick to simple pair checking and grouping.

        # Using a visited set to avoid re-processing
        # Note: 'id' might be missing, so we use object identity or index

        n = len(tx_list)
        visited = [False] * n

        for i in range(n):
            if visited[i]:
                continue

            current_group = [tx_list[i]]

            for j in range(i + 1, n):
                if visited[j]:
                    continue

                t1 = tx_list[i]
                t2 = tx_list[j]

                # Check Vendor Similarity
                vendor1 = str(t1.get('vendor', '')).lower()
                vendor2 = str(t2.get('vendor', '')).lower()

                similarity = fuzz.token_sort_ratio(vendor1, vendor2)

                if similarity > 85:
                    # Check Date proximity (optional)
                    date_match = True
                    if t1.get('date') and t2.get('date'):
                        try:
                            d1 = datetime.fromisoformat(t1['date'].replace('Z', '+00:00'))
                            d2 = datetime.fromisoformat(t2['date'].replace('Z', '+00:00'))
                            delta = abs((d1 - d2).days)
                            if delta > 7:
                                date_match = False
                        except ValueError:
                            # If date parsing fails, ignore date check (assume match or strictly require?)
                            # Requirement says "Opcional". Let's assume if dates are invalid we fallback to just name match?
                            # Or maybe skipping date check makes it stricter?
                            # Let's leniently allow it if dates are unparseable.
                            pass

                    if date_match:
                        current_group.append(t2)
                        visited[j] = True

            if len(current_group) > 1:
                suspicious_groups.append({
                    "group_id": group_counter,
                    "reason": f"Same amount ({amount}) and similar vendor (>85%)",
                    "transactions": current_group
                })
                group_counter += 1
                visited[i] = True

    return suspicious_groups
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
