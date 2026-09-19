import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_invalid_extension():
    files = {"file": ("unsupported_file.exe", b"binary content", "application/octet-stream")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_upload_empty_file():
    files = {"file": ("empty.txt", b"", "text/plain")}
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()
