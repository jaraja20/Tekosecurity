"""TEKOSECURE backend API tests."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://83ae6306-220b-4bc1-8794-cd26e51a15f9.preview.emergentagent.com").rstrip("/")
SUPABASE_URL = "https://fsucygjqzskwtnynvgob.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh"
EMAIL = "admin@gmail.com"
PASSWORD = "Tekosecure2026!"


@pytest.fixture(scope="session")
def token():
    r = requests.post(
        f"{SUPABASE_URL}/auth/v1/token",
        params={"grant_type": "password"},
        headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
        json={"email": EMAIL, "password": PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, f"Supabase login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


# --- Health ---
def test_health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "tekosecure-api"


# --- /api/me ---
def test_me_no_token():
    r = requests.get(f"{BASE_URL}/api/me", timeout=10)
    assert r.status_code == 401


def test_me_with_token(token):
    r = requests.get(f"{BASE_URL}/api/me", headers={"Authorization": f"Bearer {token}"}, timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data.get("email") == EMAIL


# --- Block IP (mocked) ---
def test_block_ip_no_auth():
    r = requests.post(f"{BASE_URL}/api/actions/block-ip", json={"attack_id": 1, "source_ip": "1.2.3.4"}, timeout=10)
    assert r.status_code == 401


def test_block_ip_success(token):
    r = requests.post(
        f"{BASE_URL}/api/actions/block-ip",
        headers={"Authorization": f"Bearer {token}"},
        json={"attack_id": 999, "source_ip": "1.2.3.4"},
        timeout=15,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "1.2.3.4" in data["message"]
    assert data["actor"] == EMAIL


# --- Close alert (uses Supabase) ---
def test_close_alert_no_auth():
    r = requests.post(f"{BASE_URL}/api/actions/close-alert", json={"attack_id": 1}, timeout=10)
    assert r.status_code == 401


def _get_active_alerts(token):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/attacks",
        params={"status": "eq.ACTIVE", "select": "id,status", "order": "id.desc"},
        headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_close_alert_flow(token):
    """Close ONE active alert and verify persistence. Leave the rest for demo."""
    active = _get_active_alerts(token)
    assert len(active) > 0, "No active alerts to close"
    target_id = active[-1]["id"]  # oldest active

    r = requests.post(
        f"{BASE_URL}/api/actions/close-alert",
        headers={"Authorization": f"Bearer {token}"},
        json={"attack_id": target_id},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["success"] is True

    # Verify persistence
    verify = requests.get(
        f"{SUPABASE_URL}/rest/v1/attacks",
        params={"id": f"eq.{target_id}", "select": "id,status"},
        headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"},
        timeout=15,
    )
    assert verify.status_code == 200
    rows = verify.json()
    assert len(rows) == 1
    assert rows[0]["status"] == "CLOSED"


# --- Seed data assertions ---
def test_seed_nvrs(token):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/hikvision_events",
        params={"select": "nvr_id,status,location", "order": "created_at.desc", "limit": "500"},
        headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    nvrs = r.json()
    latest = {}
    for row in nvrs:
        if row["nvr_id"] not in latest:
            latest[row["nvr_id"]] = row
    assert len(latest) == 9
    offline = [n for n in latest.values() if (n.get("status") or "").upper() == "OFFLINE"]
    assert len(offline) == 1
    assert offline[0]["nvr_id"] == 5
