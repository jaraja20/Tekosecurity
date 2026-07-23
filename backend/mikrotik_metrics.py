"""
TEKOSECURE — Mini-Zabbix metrics per Mikrotik

For each device we expose:
  • system    : cpu load, memory, uptime, temperature
  • isps      : per-provider status, packet loss, latency, active/backup
  • failovers : recent ISP switch events
  • vpns      : active tunnels
  • logins    : recent SSH/web login attempts

Two operating modes:
  1) DRY_RUN (default here in Emergent preview) → deterministic mock data based
     on the device name, so the UI looks alive without touching the LAN.
  2) REAL (on-prem, MIKROTIK_DRY_RUN=false) → SSH via paramiko and parse the
     output of RouterOS commands. Not implemented yet (stub raises).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Deterministic pseudo-random helpers (seeded by device name so metrics look
# stable across refreshes but differ between devices).
# ---------------------------------------------------------------------------
def _seed(name: str, salt: str = "") -> int:
    h = hashlib.md5(f"{name}::{salt}".encode()).digest()
    return int.from_bytes(h[:4], "big")


def _rand(name: str, salt: str, lo: int, hi: int) -> int:
    span = hi - lo + 1
    return lo + (_seed(name, salt) % span)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


# ---------------------------------------------------------------------------
# Per-device topology overrides (which ISPs / how many)
# ---------------------------------------------------------------------------
_ISP_TOPOLOGY: dict[str, list[dict]] = {
    "MATRIZ_KM6": [
        {"name": "Tigo Business", "gateway": "190.128.255.1", "type": "Fibra 300/100 Mbps"},
        {"name": "Personal Empresas", "gateway": "45.180.200.1", "type": "Fibra 200/100 Mbps"},
    ],
    "OASIS": [
        {"name": "Copaco Fibra", "gateway": "190.128.255.226", "type": "Fibra 100/50 Mbps"},
    ],
    "KM12": [
        {"name": "Tigo Business", "gateway": "190.128.100.1", "type": "Fibra 100/50 Mbps"},
    ],
    "HERNANDARIAS": [
        {"name": "Copaco Fibra", "gateway": "10.156.97.161", "type": "Fibra 100/50 Mbps"},
        {"name": "Tigo Business", "gateway": "45.180.150.1", "type": "Fibra 100/30 Mbps (backup)"},
    ],
}


def _isps_for(name: str) -> list[dict]:
    isps = _ISP_TOPOLOGY.get(name, [
        {"name": "ISP Primario", "gateway": "190.128.255.1", "type": "Fibra"},
    ])
    # active ISP: for HERNANDARIAS mock a recent failover to ISP2; others ISP1
    active_idx = 1 if name == "HERNANDARIAS" else 0

    out = []
    for i, isp in enumerate(isps):
        is_active = i == active_idx
        loss_pct = _rand(name, f"loss{i}", 0, 3) if is_active else _rand(name, f"loss{i}", 0, 8)
        latency = _rand(name, f"lat{i}", 8, 45)
        status = "UP" if loss_pct < 15 else "DEGRADED"
        out.append({
            **isp,
            "active": is_active,
            "packet_loss_pct": loss_pct,
            "latency_ms": latency,
            "status": status,
        })
    return out


def _failover_events(name: str) -> list[dict]:
    if name != "HERNANDARIAS":
        # 0-2 events for other devices
        events_count = _rand(name, "fev", 0, 2)
    else:
        events_count = 3  # HERNANDARIAS active on backup, so recent events

    now = _now()
    events = []
    isps = _isps_for(name)
    if len(isps) < 2:
        return []
    p, b = isps[0]["name"], isps[1]["name"]

    for i in range(events_count):
        # spread over last 12h, most recent first
        minutes_ago = _rand(name, f"fev{i}", 5, 720)
        going_to_backup = i % 2 == 0
        events.append({
            "timestamp": _iso(now - timedelta(minutes=minutes_ago)),
            "from": p if going_to_backup else b,
            "to": b if going_to_backup else p,
            "reason": "gateway unreachable" if going_to_backup else "primary link restored",
        })
    events.sort(key=lambda e: e["timestamp"], reverse=True)
    return events


def _vpns_for(name: str, role: str) -> list[dict]:
    now = _now()
    # HUB has 3 server-side tunnels; clients have 1 outbound tunnel
    if role == "VPN_SERVER_HUB":
        peers = [("OASIS", "192.168.12.1"), ("KM12", "192.168.15.1"), ("HERNANDARIAS", "192.168.16.1")]
        return [
            {
                "name": f"vpn-{peer_name.lower()}",
                "type": "L2TP/IPsec server",
                "peer": peer_ip,
                "peer_name": peer_name,
                "status": "connected",
                "uptime_hours": _rand(name, f"vpnup{peer_name}", 12, 240),
                "rx_bytes": _rand(name, f"rx{peer_name}", 50_000_000, 800_000_000),
                "tx_bytes": _rand(name, f"tx{peer_name}", 30_000_000, 400_000_000),
            }
            for peer_name, peer_ip in peers
        ]
    return [
        {
            "name": "vpn-to-matriz",
            "type": "L2TP/IPsec client",
            "peer": "190.128.255.1",
            "peer_name": "MATRIZ_KM6 (HUB)",
            "status": "connected",
            "uptime_hours": _rand(name, "vpnup", 12, 500),
            "rx_bytes": _rand(name, "rx", 50_000_000, 500_000_000),
            "tx_bytes": _rand(name, "tx", 20_000_000, 200_000_000),
        }
    ]


def _login_attempts(name: str) -> list[dict]:
    now = _now()
    n = _rand(name, "logins", 5, 12)
    out = []
    hostile_ips = ["185.220.101.42", "45.155.205.233", "103.28.36.19", "5.188.87.55"]
    for i in range(n):
        minutes_ago = _rand(name, f"login{i}", 1, 720)
        success = _rand(name, f"loginok{i}", 0, 9) < 3
        via = _rand(name, f"loginvia{i}", 0, 2)
        service = ["SSH", "Winbox", "WebFig"][via]
        if success:
            user, ip = "nasserti", f"192.168.{_rand(name, f'lip{i}', 10, 250)}.{_rand(name, f'lip2{i}', 2, 254)}"
        else:
            user = ["admin", "root", "nasserti", "test"][_rand(name, f"luser{i}", 0, 3)]
            ip = hostile_ips[_rand(name, f"lhip{i}", 0, len(hostile_ips) - 1)]
        out.append({
            "timestamp": _iso(now - timedelta(minutes=minutes_ago)),
            "user": user,
            "source_ip": ip,
            "service": service,
            "success": success,
        })
    out.sort(key=lambda e: e["timestamp"], reverse=True)
    return out


def _system_stats(name: str, priority: str) -> dict:
    return {
        "cpu_load_pct": _rand(name, "cpu", 8, 62 if priority == "CRITICAL" else 45),
        "memory_used_pct": _rand(name, "mem", 24, 68),
        "temperature_c": _rand(name, "temp", 38, 58),
        "uptime_days": _rand(name, "up", 3, 89),
        "storage_free_pct": _rand(name, "sto", 40, 88),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def collect_metrics(device: dict, dry_run: bool = True) -> dict[str, Any]:
    """
    Given a sanitized device config dict, return a snapshot of live metrics.

    In DRY_RUN we return deterministic mocks. In REAL mode this is a stub —
    will be implemented in Phase 6 with SSH queries to RouterOS.
    """
    name = device["name"]
    role = device.get("role", "VPN_CLIENT")
    priority = device.get("priority", "MEDIUM")

    if not dry_run:
        # Placeholder: on-prem impl would open MikrotikActionExecutor and run
        # /system resource print, /ip route print, /interface print, etc.
        return {
            "generated_at": _iso(_now()),
            "source": "REAL",
            "system": None,
            "isps": [],
            "failover_events": [],
            "vpns": [],
            "login_attempts": [],
            "note": "REAL metrics not implemented yet — coming in Phase 6.",
        }

    return {
        "generated_at": _iso(_now()),
        "source": "DRY_RUN",
        "system": _system_stats(name, priority),
        "isps": _isps_for(name),
        "failover_events": _failover_events(name),
        "vpns": _vpns_for(name, role),
        "login_attempts": _login_attempts(name),
    }
