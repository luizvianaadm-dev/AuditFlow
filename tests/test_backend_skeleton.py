from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "AuditFlow API"}

def test_upload_dummy():
    # Test file upload
    filename = "test_file.txt"
    file_content = b"This is a test file."
    files = {"file": (filename, file_content, "text/plain")}

    response = client.post("/upload", files=files)

    assert response.status_code == 200
    assert response.json() == {"filename": filename, "message": "File received"}
