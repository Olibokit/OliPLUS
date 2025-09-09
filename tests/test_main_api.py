# 🧪 tests/test_main_api.py — Tests des endpoints cockpit API

from fastapi.testclient import TestClient
from main_api import app
from pathlib import Path

client = TestClient(app)


def test_ping():
    res = client.get("/ping")
    assert res.status_code == 200
    assert res.json()["message"] == "pong 🏓"


def test_upload_and_archive():
    pdf_path = Path("tests/sample.pdf")
    pdf_path.write_bytes(b"%PDF-1.4\n%Fake PDF for test\n")  # contenu minimal

    with pdf_path.open("rb") as f:
        res = client.post(
            "/upload-pdf",
            data={
                "user": "olivier",
                "title": "TestDoc",
                "author": "Olivier",
                "source": "Scanner",
                "statut_cockpit": "Numérisé",
                "document_type": "Poésie"
            },
            files={"file": ("sample.pdf", f, "application/pdf")}
        )
    assert res.status_code == 200
    assert "cockpitified" in res.json()["message"]

    res2 = client.get("/archive/TestDoc")
    assert res2.status_code == 200
    assert res2.json()["metadata"]["author"] == "Olivier"
