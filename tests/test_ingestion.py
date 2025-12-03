import io
import pytest
from fastapi import UploadFile
from src.api.services.ingestion import TrialBalanceIngestion

def test_csv_ingestion_valid():
    # Emulating a Portuguese CSV with semicolon and commas
    csv_content = b"Conta;Descricao;Saldo\n1.1;Caixa;1000,00\n2.1;Fornecedores;-1000,00"
    file = UploadFile(filename="test.csv", file=io.BytesIO(csv_content))

    df = TrialBalanceIngestion.read_file(file)
    result = TrialBalanceIngestion.validate_and_parse(df)

    assert bool(result["valid"]) is True, f"Errors: {result.get('errors')}"
    assert bool(result["is_balanced"]) is True
    assert "Caixa" in result["unique_accounts"]
    assert result["net_balance"] == 0.0

def test_csv_ingestion_debit_credit():
    # Emulating Debit/Credit columns
    csv_content = b"Conta,Descricao,Debito,Credito\n1.1,Caixa,100.00,0\n2.1,Capital,0,100.00"
    file = UploadFile(filename="test.csv", file=io.BytesIO(csv_content))

    df = TrialBalanceIngestion.read_file(file)
    result = TrialBalanceIngestion.validate_and_parse(df)

    assert bool(result["valid"]) is True
    assert bool(result["is_balanced"]) is True
    assert result["total_debit"] == 100.0
    assert result["total_credit"] == 100.0

def test_csv_ingestion_unbalanced():
    csv_content = b"Conta;Descricao;Saldo\n1.1;Caixa;1000,00\n2.1;Fornecedores;-900,00"
    file = UploadFile(filename="test.csv", file=io.BytesIO(csv_content))

    df = TrialBalanceIngestion.read_file(file)
    result = TrialBalanceIngestion.validate_and_parse(df)

    assert bool(result["valid"]) is True
    assert bool(result["is_balanced"]) is False
    # 1000 - 900 = 100
    assert abs(result["net_balance"] - 100.0) < 0.01

def test_missing_columns():
    csv_content = b"A;B;C\n1;2;3"
    file = UploadFile(filename="test.csv", file=io.BytesIO(csv_content))

    df = TrialBalanceIngestion.read_file(file)
    result = TrialBalanceIngestion.validate_and_parse(df)

    assert result["valid"] is False
    assert "errors" in result
    assert any("Account Code" in e for e in result["errors"])
