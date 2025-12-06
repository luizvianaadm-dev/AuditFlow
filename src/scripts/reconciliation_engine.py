import pandas as pd
import itertools
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ReconciliationEngine:
    @staticmethod
    def parse_currency(value):
        """
        Parses Brazilian currency format (e.g., '1.000,00') to float.
        """
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove R$ and spaces
            clean_val = value.replace('R$', '').replace(' ', '')
            # Handle empty
            if not clean_val:
                return 0.0

            # Identify format:
            # If comma is present and it's the last separator, it's decimal
            # 1.000,00 -> 1000.00
            # 1000,00 -> 1000.00
            if ',' in clean_val:
                if '.' in clean_val:
                    clean_val = clean_val.replace('.', '') # remove thousands separator
                clean_val = clean_val.replace(',', '.')
            return float(clean_val)
        return 0.0

    @staticmethod
    def parse_date(value):
        """
        Parses dates, assuming DD/MM/YYYY or YYYY-MM-DD.
        Returns datetime object or None.
        """
        if pd.isna(value) or value == '':
            return None

        if isinstance(value, datetime):
            return value

        formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d']
        for fmt in formats:
            try:
                return datetime.strptime(str(value).strip(), fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def process_reconciliation(bank_df: pd.DataFrame, fin_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Reconciles Bank Statement against Financial Records using Subset Sum.

        Mappings:
        - Bank: Data, Valor, Codigo Conciliação
        - Financial: Data movimento, Valor (R$)
        """
        results = []

        # 1. Standardize Columns & Types
        # Bank
        bank_cols = {col: col.lower().strip() for col in bank_df.columns}
        # Find best matches for Data, Valor, Codigo
        # Using simple heuristics or exact names from prompt

        # Prompt: "Data", "Valor", "Codigo Conciliação"
        # We need to normalize

        def get_col(df, candidates):
            for c in df.columns:
                if c.strip() in candidates:
                    return c
            return None

        b_data = get_col(bank_df, ["Data", "Date"])
        b_valor = get_col(bank_df, ["Valor", "Value", "Amount"])
        b_code = get_col(bank_df, ["Codigo Conciliação", "Codigo", "Conciliation Code"])

        if not (b_data and b_valor and b_code):
             raise ValueError(f"Missing required columns in Bank file. Found: {list(bank_df.columns)}")

        # Fin
        # Prompt: "Data movimento", "Valor (R$)"
        f_data = get_col(fin_df, ["Data movimento", "Data Movimento", "Date"])
        f_valor = get_col(fin_df, ["Valor (R$)", "Valor", "Value"])

        if not (f_data and f_valor):
            raise ValueError(f"Missing required columns in Financial file. Found: {list(fin_df.columns)}")

        # Process Bank
        bank_clean = []
        for idx, row in bank_df.iterrows():
            code = str(row[b_code]).strip()
            # Only process rows with a code (not null/empty)
            if not code or code.lower() in ['nan', 'none', '']:
                continue

            dt = ReconciliationEngine.parse_date(row[b_data])
            val = ReconciliationEngine.parse_currency(row[b_valor])

            if dt:
                bank_clean.append({
                    "id": idx, # Original Index
                    "date": dt,
                    "amount": val,
                    "code": code,
                    "original_row": row.to_dict()
                })

        # Process Financial
        fin_clean = []
        for idx, row in fin_df.iterrows():
            dt = ReconciliationEngine.parse_date(row[f_data])
            val = ReconciliationEngine.parse_currency(row[f_valor])

            if dt:
                fin_clean.append({
                    "id": idx,
                    "date": dt,
                    "amount": val,
                    "original_row": row.to_dict()
                })

        # Group Financials by Date for faster lookup
        fin_by_date = {}
        for f in fin_clean:
            d_str = f['date'].strftime('%Y-%m-%d')
            if d_str not in fin_by_date:
                fin_by_date[d_str] = []
            fin_by_date[d_str].append(f)

        # 2. Matching Logic
        TOLERANCE = 0.01
        MAX_COMBINATIONS_R = 15
        TIMEOUT_LIMIT_OPS = 1_000_000 # Max iterations per bank line

        for b_item in bank_clean:
            d_str = b_item['date'].strftime('%Y-%m-%d')
            target_amount = b_item['amount']

            match_found = False
            matched_ids = []
            matched_details = []

            candidates = fin_by_date.get(d_str, [])

            # Optimization: Filter candidates by sign?
            # Usually Bank Debit (-) matches Financial Expense (-), or sometimes Financial is positive.
            # Assuming values are absolute or consistent.
            # Let's assume absolute matching for safety or exact match.
            # Prompt says: "soma EXATAMENTE o valor do banco".
            # If Bank is -100 and Fin are -30, -30, -40. Sum is -100.
            # If Bank is -100 and Fin are 30, 30, 40. Sum is 100.
            # We will try exact match first.

            # Heuristic: If candidates are too many (> 20), we might restrict `r`
            n = len(candidates)
            ops_count = 0

            # Try to find a subset
            # range(1, min(n + 1, MAX_COMBINATIONS_R + 1))
            limit_r = min(n + 1, MAX_COMBINATIONS_R + 1)

            for r in range(1, limit_r):
                if match_found: break

                # Safety check for complexity: C(n, r)
                # If predicted ops > limit, maybe skip this 'r' level or warn?
                # For now, we iterate and increment ops_count

                for combo in itertools.combinations(candidates, r):
                    ops_count += 1
                    if ops_count > TIMEOUT_LIMIT_OPS:
                        break # Give up on this line to save server

                    current_sum = sum(c['amount'] for c in combo)

                    if abs(current_sum - target_amount) <= TOLERANCE:
                        match_found = True
                        matched_ids = [c['id'] for c in combo]
                        matched_details = [c['original_row'] for c in combo]

                        # Remove matched items from candidates?
                        # The prompt doesn't strictly say "consume" the items (One-to-Many vs Many-to-Many uniqueness).
                        # Usually in reconciliation, once matched, it's used.
                        # But for "Algorithm that finds... matches", keeping simple logic (per line) is safer.
                        # However, strictly, if 30, 30, 40 are used for one 100, they shouldn't be used for another 100.
                        # But implementing global optimization is much harder (Knapsack/Bin Packing).
                        # We will just report the POTENTIAL match found.
                        break

                if ops_count > TIMEOUT_LIMIT_OPS:
                    logger.warning(f"Timeout reconciling Bank ID {b_item['id']} on {d_str}")
                    break

            results.append({
                "bank_entry": b_item,
                "match_found": match_found,
                "financial_matches": matched_details,
                "financial_ids": matched_ids
            })

        return results
