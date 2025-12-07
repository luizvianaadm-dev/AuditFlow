import pandas as pd
import itertools
import logging
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

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
            clean_val = value.replace('R$', '').replace(' ', '')
            if not clean_val:
                return 0.0
            if ',' in clean_val:
                if '.' in clean_val:
                    clean_val = clean_val.replace('.', '')
                clean_val = clean_val.replace(',', '.')
            try:
                return float(clean_val)
            except ValueError:
                return 0.0
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

        # Optimize: try pd.to_datetime first if applicable, but for single value loop:
        formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d']
        s_val = str(value).strip()
        for fmt in formats:
            try:
                return datetime.strptime(s_val, fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def process_reconciliation(bank_file_path: str, fin_file_path: str, output_path: str) -> str:
        """
        High-performance reconciliation engine.
        Reads files, partitions by date, and performs subset sum matching.
        Saves results to output_path (JSON).
        """
        try:
            # 1. Optimized Read
            # Use chunks if massive, but 1M rows fits in modern RAM if types are optimized.
            # We assume CSV or Excel.

            def load_df(path):
                if path.endswith('.csv'):
                    return pd.read_csv(path, low_memory=False)
                elif path.endswith(('.xls', '.xlsx')):
                    return pd.read_excel(path)
                raise ValueError("Unsupported format")

            bank_df = load_df(bank_file_path)
            fin_df = load_df(fin_file_path)

            # Column mapping helpers
            def get_col(df, candidates):
                for c in df.columns:
                    if c.strip() in candidates:
                        return c
                return None

            b_data_col = get_col(bank_df, ["Data", "Date"])
            b_valor_col = get_col(bank_df, ["Valor", "Value", "Amount"])
            b_code_col = get_col(bank_df, ["Codigo Conciliação", "Codigo", "Conciliation Code"])

            f_data_col = get_col(fin_df, ["Data movimento", "Data Movimento", "Date"])
            f_valor_col = get_col(fin_df, ["Valor (R$)", "Valor", "Value"])

            if not (b_data_col and b_valor_col and b_code_col):
                 raise ValueError("Missing Bank columns")
            if not (f_data_col and f_valor_col):
                 raise ValueError("Missing Financial columns")

            # 2. Vectorized Preprocessing
            # Bank
            bank_df['parsed_date'] = pd.to_datetime(bank_df[b_data_col], dayfirst=True, errors='coerce')
            # Custom currency parser is hard to vectorize if format varies, but we can apply map
            bank_df['parsed_amount'] = bank_df[b_valor_col].apply(ReconciliationEngine.parse_currency).astype('float32')
            bank_df['clean_code'] = bank_df[b_code_col].astype(str).str.strip()

            # Filter valid
            bank_clean = bank_df.dropna(subset=['parsed_date', 'clean_code'])
            # Exclude empty codes
            bank_clean = bank_clean[bank_clean['clean_code'] != 'nan']
            bank_clean = bank_clean[bank_clean['clean_code'] != '']

            # Financial
            fin_df['parsed_date'] = pd.to_datetime(fin_df[f_data_col], dayfirst=True, errors='coerce')
            fin_df['parsed_amount'] = fin_df[f_valor_col].apply(ReconciliationEngine.parse_currency).astype('float32')
            fin_clean = fin_df.dropna(subset=['parsed_date'])

            # Add original index to track
            bank_clean['original_idx'] = bank_clean.index
            fin_clean['original_idx'] = fin_clean.index

            # 3. Partitioning (Group by Date)
            # Create a dictionary of Financial items keyed by Date
            # Optimization: Groupby object
            fin_groups = fin_clean.groupby(fin_clean['parsed_date'].dt.date)

            # Convert to dict for fast access {date: df_group}
            # Actually, iterating matches is better done per Bank group as well?
            # Yes: match Bank(Date X) with Fin(Date X).

            bank_groups = bank_clean.groupby(bank_clean['parsed_date'].dt.date)

            results = []

            TOLERANCE = 0.01
            MAX_COMBINATIONS = 15
            MAX_CANDIDATES_SOFT_LIMIT = 100

            for date_key, b_group in bank_groups:
                if date_key not in fin_groups.groups:
                    continue # No financials for this date

                f_group = fin_groups.get_group(date_key)

                # Convert financial candidates to list of tuples for speed: (id, amount)
                # Sort by amount descending (heuristic for subset sum)
                all_candidates = list(zip(f_group['original_idx'], f_group['parsed_amount']))

                # Optimisation: If candidates > 100, we truncate?
                # Or we just rely on the loop breaker.
                # Let's keep all but be aggressive on breaker.

                # Process each bank item in this date
                for _, b_row in b_group.iterrows():
                    target = b_row['parsed_amount']
                    b_id = b_row['original_idx']
                    b_code = b_row['clean_code']

                    # Subset Sum
                    match_found = False
                    matched_ids = []

                    # Optimization: Filter candidates by magnitude
                    # Assuming items sum up to target, magnitude of each item <= magnitude of target (with tolerance)
                    # This is safe for standard splitting.
                    target_abs = abs(target) + TOLERANCE
                    candidates = [c for c in all_candidates if abs(c[1]) <= target_abs]

                    # Sort candidates descending
                    candidates.sort(key=lambda x: x[1], reverse=True)

                    # Limit r range
                    limit_r = min(len(candidates) + 1, MAX_COMBINATIONS + 1)

                    # Heuristic: if len(candidates) is huge, this is O(2^N).
                    # We MUST limit the iterations count per item.
                    ITER_LIMIT = 50_000
                    iter_count = 0

                    for r in range(1, limit_r):
                        if match_found: break

                        # Optimization: Check bounds
                        # candidates are sorted descending.
                        # Max possible sum with r items = first r items
                        # Min possible sum with r items = last r items
                        if len(candidates) >= r:
                            max_possible = sum(c[1] for c in candidates[:r])
                            min_possible = sum(c[1] for c in candidates[-r:])

                            # Assuming target and candidates are mostly positive/consistent signs
                            # If mixed signs, this heuristic is risky.
                            # But for standard reconciliation (Payments), signs usually match.
                            # We apply it only if all candidates are positive or we accept the risk of skipping.
                            # Given the prompt's context, let's assume loose heuristic is better than timeout.

                            if target > max_possible + TOLERANCE:
                                # Target is too big for any combo of size r
                                continue
                            if target < min_possible - TOLERANCE:
                                # Target is too small for any combo of size r
                                continue

                        for combo in itertools.combinations(candidates, r):
                            iter_count += 1
                            if iter_count > ITER_LIMIT:
                                break

                            current_sum = sum(item[1] for item in combo)

                            if abs(current_sum - target) <= TOLERANCE:
                                match_found = True
                                matched_ids = [item[0] for item in combo]
                                break

                        if iter_count > ITER_LIMIT:
                            break

                    if match_found:
                        results.append({
                            "bank_id": int(b_id),
                            "bank_code": b_code,
                            "date": str(date_key),
                            "target_amount": float(target),
                            "matched_fin_ids": [int(mid) for mid in matched_ids]
                        })

                        # Greedy Approach? Should we remove matched items?
                        # "Filtre as linhas do Financeiro ... que ainda não têm Codigo".
                        # Since we are processing a batch, we don't have the 'code' status update in real-time in the DF.
                        # For high accuracy, we SHOULD remove them from 'candidates' for subsequent bank items in the same day.
                        # Let's do that.
                        used_ids = set(matched_ids)
                        all_candidates = [c for c in all_candidates if c[0] not in used_ids]

            # 4. Save Results
            results_df = pd.DataFrame(results)
            results_df.to_json(output_path, orient='records', indent=2)

            return output_path

        except Exception as e:
            logger.error(f"Reconciliation failed: {e}")
            raise e
