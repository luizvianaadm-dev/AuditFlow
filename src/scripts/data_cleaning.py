import pandas as pd
import io
import re
from typing import List, Dict, Optional, Tuple

class DataCleaner:
    REQUIRED_COLUMNS = {
        'account_code': ['cod', 'codigo', 'conta', 'account_code', 'code'],
        'description': ['descricao', 'desc', 'historico', 'nome', 'description', 'account_name'],
        'balance': ['saldo', 'valor', 'balance', 'amount', 'saldo_final']
    }

    def __init__(self, file_content: bytes, filename: str):
        self.content = file_content
        self.filename = filename
        self.df: Optional[pd.DataFrame] = None
        self.encoding = 'utf-8'
        self.separator = ','
        self.skiprows = 0

    def detect_encoding(self) -> str:
        # Simple heuristic
        try:
            self.content.decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            return 'latin-1' # Common in Brazil

    def detect_separator(self, line: str) -> str:
        if ';' in line: return ';'
        if '\t' in line: return '\t'
        return ','

    def find_header_row(self, sample_lines: List[str]) -> int:
        # Look for a line that contains at least 2 potential column headers
        for i, line in enumerate(sample_lines):
            line_lower = line.lower()
            matches = 0
            for keywords in self.REQUIRED_COLUMNS.values():
                if any(k in line_lower for k in keywords):
                    matches += 1
            if matches >= 2:
                return i
        return 0

    def load_dataframe(self):
        self.encoding = self.detect_encoding()
        decoded_sample = self.content[:2048].decode(self.encoding, errors='ignore')
        sample_lines = decoded_sample.splitlines()

        self.separator = self.detect_separator(sample_lines[0] if sample_lines else '')
        self.skiprows = self.find_header_row(sample_lines[:20]) # Check first 20 lines

        self.df = pd.read_csv(
            io.BytesIO(self.content),
            sep=self.separator,
            skiprows=self.skiprows,
            encoding=self.encoding,
            on_bad_lines='skip',
            dtype=str  # Read all as string to preserve leading zeros
        )

    def standardize_columns(self) -> List[str]:
        if self.df is None: return []

        normalized_cols = {c: c.lower().strip() for c in self.df.columns}
        rename_map = {}

        found_cols = []

        for target, keywords in self.REQUIRED_COLUMNS.items():
            for col_original, col_lower in normalized_cols.items():
                if any(k in col_lower for k in keywords):
                    rename_map[col_original] = target
                    found_cols.append(target)
                    break

        self.df.rename(columns=rename_map, inplace=True)
        return found_cols

    def clean_data(self):
        if self.df is None: return

        # Drop rows where critical columns are NaN
        critical_cols = [c for c in ['account_code', 'description'] if c in self.df.columns]
        if critical_cols:
            self.df.dropna(subset=critical_cols, how='all', inplace=True)

        # Remove rows that look like footers (e.g. "Total", "Saldo Final") in description
        if 'description' in self.df.columns:
            # Filter rows where description contains "Total" or "Saldo" and code is empty or weird
            mask = self.df['description'].str.contains('Total|Saldo', case=False, na=False)
            # This is a bit aggressive, maybe just flag them?
            # For now, let's keep simple: drop if account_code is missing AND description implies footer
            if 'account_code' in self.df.columns:
                 mask_footer = mask & (self.df['account_code'].isna() | (self.df['account_code'] == ''))
                 self.df = self.df[~mask_footer]

        # Clean numeric columns (balance)
        if 'balance' in self.df.columns:
            self.df['balance'] = self.df['balance'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            # Handle (100.00) or 100.00 D/C formatting later?
            # For now, just ensure it's numeric-ish
            self.df['balance'] = pd.to_numeric(self.df['balance'], errors='coerce').fillna(0)

    def process(self) -> pd.DataFrame:
        self.load_dataframe()
        self.standardize_columns()
        self.clean_data()
        return self.df.head(50) # Return preview
