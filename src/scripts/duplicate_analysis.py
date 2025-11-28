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
