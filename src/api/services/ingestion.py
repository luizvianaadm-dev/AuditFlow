import pandas as pd
import io
from fastapi import UploadFile, HTTPException
from typing import Dict, Any, List

class TrialBalanceIngestion:
    @staticmethod
    def read_file(file: UploadFile) -> pd.DataFrame:
        # Read file content into memory
        content = file.file.read()
        filename = file.filename.lower()

        try:
            if filename.endswith('.csv'):
                # Try utf-8 first, then latin-1 with different separators
                try:
                    # Detect separator simply
                    try_str = content[:1024].decode('utf-8')
                except:
                    try_str = content[:1024].decode('latin-1')

                sep = ';' if ';' in try_str and try_str.count(';') > try_str.count(',') else ','

                try:
                    df = pd.read_csv(io.BytesIO(content), encoding='utf-8', sep=sep)
                except UnicodeDecodeError:
                    df = pd.read_csv(io.BytesIO(content), encoding='latin-1', sep=sep)

            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            elif filename.endswith('.xls'):
                df = pd.read_excel(io.BytesIO(content), engine='xlrd')
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV, XLSX, or XLS.")

            return df
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    @staticmethod
    def validate_and_parse(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validates the dataframe and returns structured data.
        """
        # Normalize headers
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Heuristics for column detection
        col_map = {
            'account_code': ['account', 'conta', 'codigo', 'código', 'cod', 'acct'],
            'description': ['description', 'descric', 'descrição', 'nome', 'historico', 'name'],
            'balance': ['balance', 'saldo', 'valor', 'amount', 'total'],
            'debit': ['debit', 'debito', 'débito', 'debitos'],
            'credit': ['credit', 'credito', 'crédito', 'creditos']
        }

        found_cols = {}
        for key, patterns in col_map.items():
            for col in df.columns:
                if any(p in col for p in patterns):
                    found_cols[key] = col
                    break

        # Validation Errors
        errors = []
        if 'account_code' not in found_cols:
            errors.append("Missing 'Account Code' column (e.g., Conta, Codigo).")
        if 'description' not in found_cols:
            errors.append("Missing 'Description' column (e.g., Descricao, Nome).")

        has_balance = 'balance' in found_cols
        has_dc = 'debit' in found_cols and 'credit' in found_cols

        if not (has_balance or has_dc):
             errors.append("Missing financial columns (Balance OR Debit/Credit).")

        if errors:
            return {"valid": False, "errors": errors}

        # Data Cleaning & Calculation
        def clean_currency(x):
            if pd.isna(x): return 0.0
            if isinstance(x, (int, float)): return float(x)
            if isinstance(x, str):
                x = x.strip().replace('R$', '').replace(' ', '')
                # Detect format: 1.000,00 (BR) vs 1,000.00 (US)
                if ',' in x and '.' in x:
                    if x.rfind(',') > x.rfind('.'): # BR: 1.000,00
                         x = x.replace('.', '').replace(',', '.')
                    else: # US: 1,000.00
                         x = x.replace(',', '')
                elif ',' in x: # BR without thousands: 1000,00
                    x = x.replace(',', '.')
                try:
                    return float(x)
                except ValueError:
                    return 0.0
            return 0.0

        total_debit = 0.0
        total_credit = 0.0
        net_balance = 0.0

        # Create normalized dataframe subset
        normalized_data = pd.DataFrame()
        normalized_data['account_code'] = df[found_cols['account_code']].astype(str).str.strip()
        normalized_data['description'] = df[found_cols['description']].astype(str).str.strip()

        if has_dc:
            d_col = found_cols['debit']
            c_col = found_cols['credit']
            df['clean_debit'] = df[d_col].apply(clean_currency)
            df['clean_credit'] = df[c_col].apply(clean_currency)

            total_debit = df['clean_debit'].sum()
            total_credit = df['clean_credit'].sum()
            net_balance = total_debit - total_credit

            normalized_data['debit'] = df['clean_debit']
            normalized_data['credit'] = df['clean_credit']
            normalized_data['balance'] = df['clean_debit'] - df['clean_credit']
        elif has_balance:
            b_col = found_cols['balance']
            df['clean_balance'] = df[b_col].apply(clean_currency)
            net_balance = df['clean_balance'].sum()

            normalized_data['balance'] = df['clean_balance']

        is_balanced = abs(net_balance) < 0.05 # 5 cents tolerance

        return {
            "valid": True,
            "is_balanced": is_balanced,
            "net_balance": net_balance,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "unique_accounts": normalized_data['description'].unique().tolist(),
            # "normalized_data": normalized_data.to_dict(orient='records') # Keep payload small for now
        }
