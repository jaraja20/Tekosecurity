#!/usr/bin/env python3
"""
TEKOSECURE — Seed Supabase with 9 NVRs and sample attacks/events for demo.
Idempotent: only inserts if tables are empty (or per-nvr for NVRs).

Run once locally:
    python3 /app/scripts/seed_supabase.py
"""

import os
import random
from datetime import datetime, timedelta, timezone

import httpx

SUPABASE_URL = "https://fsucygjqzskwtnynvgob.supabase.co"
SUPABASE_KEY = "sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

NVRS = [
    {"nvr_id": 1, "nvr_name": "Matriz KM6 - Principal",  "nvr_ip": "192.168.13.188", "model": "DS-7216HUHI-K2",    "port_count": 16, "location": "Casa Matriz"},
    {"nvr_id": 2, "nvr_name": "Matriz KM6 - Depósito",   "nvr_ip": "192.168.13.20",  "model": "DS-7616NI-Q2",      "port_count": 16, "location": "Casa Matriz"},
    {"nvr_id": 3, "nvr_name": "Depósito KM7",            "nvr_ip": "192.168.2.10",   "model": "DS-7732NXI-K4(D)",  "port_count": 32, "location": "Depósito KM7"},
    {"nvr_id": 4, "nvr_name": "Oasis - Centro",          "nvr_ip": "192.168.12.244", "model": "DS-7632NI-K2",      "port_count": 32, "location": "Oasis"},
    {"nvr_id": 5, "nvr_name": "Zona Franca Global - NVR1","nvr_ip": "192.168.15.252","model": "iDS-7616NXI-M2/X",  "port_count": 16, "location": "Zona Franca Global"},
    {"nvr_id": 6, "nvr_name": "Zona Franca Global - NVR2","nvr_ip": "192.168.15.250","model": "iDS-7616NXI-M2/X",  "port_count": 16, "location": "Zona Franca Global"},
    {"nvr_id": 7, "nvr_name": "Hernandarias",            "nvr_ip": "192.168.16.177", "model": "iDS-7616NXI-M2/X",  "port_count": 16, "location": "Hernandarias"},
    {"nvr_id": 8, "nvr_name": "Ypane - Principal",       "nvr_ip": "192.168.3.253",  "model": "iDS-7616NXI-M2/X",  "port_count": 16, "location": "Ypane"},
    {"nvr_id": 9, "nvr_name": "Ypane - Depósito",        "nvr_ip": "192.168.3.215",  "model": "iDS-7616NXI-M2/X",  "port_count": 16, "location": "Ypane"},
]

OFFLINE_IDS = {5}  # Zona Franca Global - NVR1 offline for demo

ATTACK_TYPES = [
    ("BRUTE_FORCE",       "CRITICAL", "12 intentos SSH fallidos en 3 min desde IP externa"),
    ("BRUTE_FORCE",       "HIGH",     "5 intentos de login RDP fallidos en 5 min"),
    ("DDoS",              "CRITICAL", "Tasa anómala 14.500 paq/seg hacia gateway"),
    ("PORT_SCAN",         "MEDIUM",   "Scan detectado en 24 puertos (nmap SYN scan)"),
    ("ANOMALOUS_TRAFFIC", "HIGH",     "Uso de banda 92% en interfaz ether1 durante 8 min"),
    ("NVR_OFFLINE",       "HIGH",     "NVR sin responder ping durante 4 min consecutivos"),
    ("PORT_SCAN",         "LOW",      "Escaneo lento detectado en 5 puertos"),
    ("BRUTE_FORCE",       "MEDIUM",   "Intentos de acceso al panel web de Hikvision"),
]

SOURCE_IPS = [
    "185.220.101.42", "45.155.205.233", "103.28.36.19",
    "192.168.1.50", "104.28.6.121", "5.188.87.55",
    "192.168.15.252",
]


def get(url: str, params: dict | None = None):
    r = httpx.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def post(url: str, payload):
    r = httpx.post(url, headers=HEADERS, json=payload, timeout=15)
    if r.status_code >= 400:
        raise RuntimeError(f"POST {url} -> {r.status_code} {r.text}")
    return r.json()


def seed_nvrs():
    print("→ Seeding NVR status rows...")
    now = datetime.now(timezone.utc)
    rows = []
    for nvr in NVRS:
        status = "OFFLINE" if nvr["nvr_id"] in OFFLINE_IDS else "ONLINE"
        rows.append({
            **nvr,
            "event_type": "STATUS_CHECK",
            "status": status,
            "created_at": (now - timedelta(minutes=random.randint(1, 4))).isoformat(),
            "details": f"{status} — chequeo automático",
        })
    post(f"{SUPABASE_URL}/rest/v1/hikvision_events", rows)
    print(f"  ✓ Inserted {len(rows)} hikvision_events")


def seed_attacks():
    print("→ Seeding attacks (mixed active/closed)...")
    now = datetime.now(timezone.utc)
    rows = []
    # 6 ACTIVE (today, spread across last few hours)
    for i in range(6):
        at, sev, det = random.choice(ATTACK_TYPES)
        rows.append({
            "attack_type": at,
            "severity": sev,
            "source_ip": random.choice(SOURCE_IPS),
            "destination_ip": "192.168.13.100",
            "mikrotik_ip": "192.168.13.100",
            "status": "ACTIVE",
            "details": det,
            "created_at": (now - timedelta(minutes=random.randint(2, 260))).isoformat(),
        })
    # 9 CLOSED historical
    for i in range(9):
        at, sev, det = random.choice(ATTACK_TYPES)
        rows.append({
            "attack_type": at,
            "severity": sev,
            "source_ip": random.choice(SOURCE_IPS),
            "destination_ip": "192.168.13.100",
            "mikrotik_ip": "192.168.13.100",
            "status": "CLOSED",
            "details": det,
            "created_at": (now - timedelta(hours=random.randint(2, 96))).isoformat(),
        })
    post(f"{SUPABASE_URL}/rest/v1/attacks", rows)
    print(f"  ✓ Inserted {len(rows)} attacks")


def main():
    print("=" * 60)
    print("TEKOSECURE — Supabase seed")
    print("=" * 60)

    existing_nvrs = get(f"{SUPABASE_URL}/rest/v1/hikvision_events", {"select": "id", "limit": "1"})
    existing_attacks = get(f"{SUPABASE_URL}/rest/v1/attacks", {"select": "id", "limit": "1"})

    if not existing_nvrs:
        seed_nvrs()
    else:
        print("→ hikvision_events not empty, skipping NVR seed")

    if not existing_attacks:
        seed_attacks()
    else:
        print("→ attacks not empty, skipping attack seed")

    print("✓ Done")


if __name__ == "__main__":
    main()
