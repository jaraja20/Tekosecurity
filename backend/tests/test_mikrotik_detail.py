"""Tests for GET /api/mikrotiks/{name} — Phase 6 mini-Zabbix per-device metrics."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://emergent-security-1.preview.emergentagent.com").rstrip("/")
SUPABASE_URL = "https://fsucygjqzskwtnynvgob.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh"
EMAIL = "ti@nasser.com.py"
PASSWORD = "NasserTi73491654"


@pytest.fixture(scope="module")
def token():
    r = requests.post(
        f"{SUPABASE_URL}/auth/v1/token",
        params={"grant_type": "password"},
        headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
        json={"email": EMAIL, "password": PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, f"Login failed: {r.text}"
    return r.json()["access_token"]


def _get(name, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{BASE_URL}/api/mikrotiks/{name}", headers=headers, timeout=15)


def test_detail_no_auth():
    r = _get("HERNANDARIAS")
    assert r.status_code == 401


def test_detail_unknown_device(token):
    r = _get("UNKNOWN_DEVICE", token)
    assert r.status_code == 404
    assert "detail" in r.json()


def test_detail_case_insensitive(token):
    r = _get("hernandarias", token)
    assert r.status_code == 200
    assert r.json()["device"]["name"] == "HERNANDARIAS"


def test_hernandarias_detail(token):
    r = _get("HERNANDARIAS", token)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["device"]["name"] == "HERNANDARIAS"
    assert "password" not in d["device"]
    assert "password" not in r.text.lower()
    assert d["mode"] == "DRY_RUN"

    m = d["metrics"]
    assert m["source"] == "DRY_RUN"

    # system keys
    sys = m["system"]
    for k in ("cpu_load_pct", "memory_used_pct", "temperature_c", "uptime_days", "storage_free_pct"):
        assert k in sys, f"missing key {k}"

    # isps: 2 items, exactly 1 active
    assert isinstance(m["isps"], list) and len(m["isps"]) == 2
    active = [i for i in m["isps"] if i.get("active")]
    assert len(active) == 1

    # failover events >=1 (HERNANDARIAS mock has 3)
    assert isinstance(m["failover_events"], list)
    assert len(m["failover_events"]) >= 1

    # vpns >=1
    assert isinstance(m["vpns"], list) and len(m["vpns"]) >= 1

    # login_attempts >=5
    assert isinstance(m["login_attempts"], list) and len(m["login_attempts"]) >= 5


def test_matriz_km6_detail(token):
    r = _get("MATRIZ_KM6", token)
    assert r.status_code == 200
    d = r.json()
    assert d["device"]["role"] == "VPN_SERVER_HUB"
    m = d["metrics"]
    assert len(m["isps"]) == 2
    isp_names = {i["name"] for i in m["isps"]}
    assert "Tigo Business" in isp_names
    assert "Personal Empresas" in isp_names
    # 3 vpn server tunnels
    assert len(m["vpns"]) == 3
    for v in m["vpns"]:
        assert v["type"] == "L2TP/IPsec server"
    peer_names = {v["peer_name"] for v in m["vpns"]}
    assert peer_names == {"OASIS", "KM12", "HERNANDARIAS"}


def test_oasis_detail(token):
    r = _get("OASIS", token)
    assert r.status_code == 200
    m = r.json()["metrics"]
    assert len(m["isps"]) == 1
    assert m["isps"][0]["name"] == "Copaco Fibra"
    assert len(m["vpns"]) == 1
    assert m["vpns"][0]["type"] == "L2TP/IPsec client"


def test_determinism(token):
    r1 = _get("HERNANDARIAS", token).json()["metrics"]
    r2 = _get("HERNANDARIAS", token).json()["metrics"]
    # everything equal except generated_at
    for key in ("system", "isps", "failover_events", "vpns", "login_attempts"):
        assert r1[key] == r2[key], f"{key} not deterministic"


def test_no_password_leak_all(token):
    for name in ("MATRIZ_KM6", "OASIS", "KM12", "HERNANDARIAS"):
        r = _get(name, token)
        assert r.status_code == 200
        assert "password" not in r.text.lower(), f"password leaked in {name}"
        assert "password" not in r.json()["device"]
