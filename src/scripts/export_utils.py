import pandas as pd
import io

def export_to_excel(dataframes, sheet_names=None):
    """
    Exports a list of DataFrames to an Excel file with multiple sheets.
    dataframes: List of pd.DataFrame
    sheet_names: List of str (optional)
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for i, df in enumerate(dataframes):
            name = sheet_names[i] if sheet_names and i < len(sheet_names) else f"Sheet{i+1}"
            df.to_excel(writer, sheet_name=name, index=False)

    output.seek(0)
    return output

def export_to_csv(dataframe):
    output = io.StringIO()
    dataframe.to_csv(output, index=False)
    return io.BytesIO(output.getvalue().encode('utf-8'))

def benford_to_df(result):
    details = result.get('details', [])
    df = pd.DataFrame(details)
    # Reorder/Rename
    if not df.empty:
        df = df[['digit', 'expected', 'observed', 'deviation', 'is_anomaly']]
        df.columns = ['Dígito', 'Esperado', 'Observado', 'Desvio', 'Anomalia']
    return df

def duplicates_to_df(result):
    groups = result.get('duplicates', [])
    rows = []
    for i, group in enumerate(groups):
        group_id = i + 1
        amount = group.get('amount')
        score = group.get('similarity_score')

        for tx in group.get('transactions', []):
            rows.append({
                'Grupo': group_id,
                'Valor do Grupo': amount,
                'Similaridade (%)': score,
                'ID Transação': tx.get('id'),
                'Fornecedor': tx.get('vendor'),
                'Data': tx.get('date')
            })

    return pd.DataFrame(rows)

def transactions_to_df(transactions):
    # transactions is a list of SQLAlchemy objects or dicts
    rows = []
    for t in transactions:
        # Check if object or dict
        if hasattr(t, '__dict__'):
            row = {
                'ID': t.id,
                'Data': t.date,
                'Fornecedor': t.vendor,
                'Valor': t.amount,
                'Descrição': t.description,
                'Conta': t.account_code,
                'Nome da Conta': t.account_name
            }
        else:
            row = t
        rows.append(row)
    return pd.DataFrame(rows)

def mistatements_to_df(mistatements):
    rows = []
    for m in mistatements:
        rows.append({
            'Descrição': m.description,
            'Valor (Divergência)': m.amount_divergence,
            'Tipo': m.type,
            'Status': m.status
        })
    return pd.DataFrame(rows)
