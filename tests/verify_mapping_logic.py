import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.getcwd())

from src.api.main import app
from src.api.database import Base, get_db
from src.api import models
from src.api import deps

# Setup In-Memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_mapping.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Setup Auth bypass (mock user)
def override_get_current_user():
    db = TestingSessionLocal()
    user = db.query(models.User).filter(models.User.email == "test@example.com").first()
    db.close()
    return user

app.dependency_overrides[deps.get_current_user] = override_get_current_user

client = TestClient(app)

def setup_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    # Create Firm
    firm = models.AuditFirm(name="Test Firm", cnpj="12345678901234")
    db.add(firm)
    db.commit()

    # Create User
    user = models.User(email="test@example.com", firm_id=firm.id, role="auditor")
    db.add(user)
    db.commit()

    # Create Client
    client_obj = models.Client(name="Test Client", firm_id=firm.id)
    db.add(client_obj)
    db.commit()

    # Create Engagement
    engagement = models.Engagement(
        name="Test Engagement",
        year=2024,
        client_id=client_obj.id,
        service_type="br_gaap",
        chart_mode="standard_auditflow" # Default
    )
    db.add(engagement)
    db.commit()

    # Create Transactions (Simulate Upload)
    t1 = models.Transaction(engagement_id=engagement.id, account_code="1001", account_name="Caixa", amount=100.0)
    t2 = models.Transaction(engagement_id=engagement.id, account_code="2001", account_name="Fornecedores", amount=-50.0)
    db.add(t1)
    db.add(t2)
    db.commit()

    db.close()
    return engagement.id

def test_verify_mapping_flow():
    engagement_id = setup_data()

    # 1. Seed Accounts (we need to call the seed function or assume it's done.
    # Since we are using a fresh sqlite file, we must seed it here manually or import the script logic)

    db = TestingSessionLocal()
    std = models.StandardAccount(code="1.1.1.01", name="Caixa Geral", template_type="br_gaap")
    db.add(std)
    db.commit()
    std_id = std.id
    db.close()

    # 2. Get Standard Accounts
    response = client.get("/mapping/standard-accounts?template_type=br_gaap")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["code"] == "1.1.1.01"

    # 3. Get Mapping Context
    response = client.get(f"/mapping/{engagement_id}")
    assert response.status_code == 200
    data = response.json()
    assert "client_accounts" in data
    assert len(data["client_accounts"]) == 2
    assert "standard_accounts" in data
    assert "mappings" in data
    assert data["chart_mode"] == "standard_auditflow"

    # 4. Set Standard Mode (Switch to client custom)
    response = client.post(f"/mapping/{engagement_id}/set-standard?chart_mode=client_custom")
    assert response.status_code == 200
    assert response.json()["chart_mode"] == "client_custom"

    # Verify context changed (should return no standard accounts if none created for client yet)
    response = client.get(f"/mapping/{engagement_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["chart_mode"] == "client_custom"
    # standard_accounts might be empty unless we saved as standard

    # 5. Save as Standard (Client Custom)
    response = client.post(f"/mapping/{engagement_id}/save-as-standard")
    assert response.status_code == 200
    assert "Created" in response.json()["message"]

    # Verify context again
    response = client.get(f"/mapping/{engagement_id}")
    data = response.json()
    assert len(data["standard_accounts"]) == 2 # "Caixa" and "Fornecedores" created as standard

    # 6. Create Mapping (Bulk)
    # Let's switch back to AuditFlow Standard for mapping test
    client.post(f"/mapping/{engagement_id}/set-standard?chart_mode=standard_auditflow")

    # Test Bulk Mapping
    bulk_payload = [
        {
            "client_description": "Caixa",
            "client_account_code": "1001",
            "standard_account_id": std_id
        },
        {
            "client_description": "Fornecedores",
            "client_account_code": "2001",
            "standard_account_id": std_id # Mapping both to same just for test
        }
    ]

    response = client.post("/mapping/bulk-map", json=bulk_payload)
    assert response.status_code == 201
    assert "Successfully processed 2 mappings" in response.json()["message"]

    # 7. Verify Persistence
    response = client.get("/mapping/firm-mappings")
    assert response.status_code == 200
    mappings = response.json()
    assert len(mappings) == 2

    codes = [m["client_account_code"] for m in mappings]
    assert "1001" in codes
    assert "2001" in codes

    print("Mapping Flow Verified Successfully!")

if __name__ == "__main__":
    test_verify_mapping_flow()
