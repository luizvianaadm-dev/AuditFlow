import httpx
import os
import json

ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "")
ASAAS_URL = os.getenv("ASAAS_URL", "https://sandbox.asaas.com/api/v3")

headers = {
    "access_token": ASAAS_API_KEY,
    "Content-Type": "application/json"
}

async def create_customer(name: str, email: str, cpf_cnpj: str):
    """
    Creates or retrieves a customer in Asaas.
    """
    if not ASAAS_API_KEY:
        print("Warning: ASAAS_API_KEY not set. Mocking customer creation.")
        return "cus_mock_123"

    async with httpx.AsyncClient() as client:
        # First check if exists (simplification: search by email)
        response = await client.get(f"{ASAAS_URL}/customers?email={email}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                return data["data"][0]["id"]
        
        # Create new
        payload = {
            "name": name,
            "email": email,
            "cpfCnpj": cpf_cnpj
        }
        response = await client.post(f"{ASAAS_URL}/customers", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()["id"]
        else:
            print(f"Error creating Asaas customer: {response.text}")
            return None

async def create_payment(customer_id: str, value: float, description: str, due_date_str: str = None):
    """
    Creates a new payment (Cobrança) and returns the invoice URL.
    """
    if not ASAAS_API_KEY:
        print("Warning: ASAAS_API_KEY not set. Mocking payment creation.")
        return "https://sandbox.asaas.com/fat/mock_invoice_url"

    if not due_date_str:
        from datetime import datetime, timedelta
        due_date_str = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    payload = {
        "customer": customer_id,
        "billingType": "UNDEFINED", # Allows user to choose Pix/Boleto/Card
        "value": value,
        "dueDate": due_date_str,
        "description": description
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{ASAAS_URL}/payments", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()["invoiceUrl"]
        else:
            print(f"Error creating Asaas payment: {response.text}")
            raise Exception(f"Failed to create payment: {response.text}")
