import pytest
import json
import sys
import os

# Ajoute le dossier parent au path pour importer app.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app

# ─── Configuration du client de test ──────────────────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ─── Tests route / ────────────────────────────────────────────────────────────
def test_index_status_ok(client):
    """La route / doit retourner HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_index_contenu(client):
    """La route / doit retourner status=ok et version=1.0.0."""
    response = client.get("/")
    data = json.loads(response.data)
    assert data["status"]  == "ok"
    assert data["version"] == "1.0.0"


# ─── Tests route /health ──────────────────────────────────────────────────────
def test_health_status_ok(client):
    """La route /health doit retourner HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_contenu(client):
    """La route /health doit retourner status=healthy et un timestamp."""
    response = client.get("/health")
    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert "timestamp"    in data


# ─── Tests route /event ───────────────────────────────────────────────────────
def test_event_sans_body(client):
    """La route /event sans JSON doit retourner HTTP 400."""
    response = client.post("/event", content_type="application/json")
    assert response.status_code == 400


def test_event_avec_body(client):
    """La route /event avec JSON valide doit retourner HTTP 201."""
    payload  = {"type": "test", "message": "evenement de test"}
    response = client.post(
        "/event",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 201


def test_event_contenu_retourne(client):
    """La route /event doit retourner l'événement dans la réponse."""
    payload  = {"type": "deploy", "service": "flask-app"}
    response = client.post(
        "/event",
        data=json.dumps(payload),
        content_type="application/json"
    )
    data = json.loads(response.data)
    assert "event"  in data
    assert "status" in data


# ─── Tests route /metrics ─────────────────────────────────────────────────────
def test_metrics_disponibles(client):
    """La route /metrics doit retourner HTTP 200."""
    response = client.get("/metrics")
    assert response.status_code == 200
