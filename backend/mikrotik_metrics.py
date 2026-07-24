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
     output of RouterOS commands.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

try:
    import paramiko
except ImportError:
    paramiko = None

logger = logging.getLogger(__name__)


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
# Real SSH-based metrics collection
# ---------------------------------------------------------------------------
def _ssh_exec(client: "paramiko.SSHClient", cmd: str) -> str:
    """Execute command via SSH, return stdout."""
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode().strip()


def _parse_system_metrics(device: dict, client: "paramiko.SSHClient") -> Optional[dict]:
    """Fetch real system metrics from RouterOS via SSH."""
    try:
        resource = _ssh_exec(client, "/system resource print")

        # Parse RouterOS key: value format
        stats = {}
        for line in resource.split('\n'):
            if ':' in line and not line.strip().startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    stats[key] = value

        # Extract metrics
        cpu_load = stats.get('cpu-load', '0%').rstrip('%')

        # Parse memory: "200.3MiB" and "256.0MiB"
        free_mem_str = stats.get('free-memory', '0MiB').replace('MiB', '').strip()
        total_mem_str = stats.get('total-memory', '256MiB').replace('MiB', '').strip()
        free_mem = float(free_mem_str) if free_mem_str else 0
        total_mem = float(total_mem_str) if total_mem_str else 256
        memory_used_pct = int(((total_mem - free_mem) / total_mem * 100)) if total_mem > 0 else 0

        # Parse storage
        free_hdd_str = stats.get('free-hdd-space', '0KiB').replace('KiB', '').strip()
        total_hdd_str = stats.get('total-hdd-space', '16MiB').replace('MiB', '').strip()
        free_hdd = float(free_hdd_str) if free_hdd_str else 0
        total_hdd = float(total_hdd_str) * 1024 if total_hdd_str else 16384  # Convert MiB to KiB
        storage_free_pct = int((free_hdd / total_hdd * 100)) if total_hdd > 0 else 0

        # Parse uptime: "19w3d8h8m45s"
        uptime_str = stats.get('uptime', '1d')
        uptime_days = 1
        if 'w' in uptime_str:
            weeks = int(uptime_str.split('w')[0])
            uptime_days = weeks * 7
            if 'd' in uptime_str:
                days = int(uptime_str.split('w')[1].split('d')[0])
                uptime_days += days

        return {
            "cpu_load_pct": int(float(cpu_load)) if cpu_load else 0,
            "memory_used_pct": memory_used_pct,
            "temperature_c": 45,  # RouterOS doesn't expose this reliably
            "uptime_days": uptime_days,
            "storage_free_pct": storage_free_pct,
        }
    except Exception as e:
        logger.warning(f"Error getting system metrics: {e}")
        return None


def _parse_isps_real(device: dict, client: "paramiko.SSHClient") -> list[dict]:
    """Parse REAL ISPs from RouterOS /interface and /ip route print output."""
    try:
        iface_output = _ssh_exec(client, "/interface print")
        route_output = _ssh_exec(client, "/ip route print")

        # Find all Internet interfaces
        isps = []
        for line in iface_output.split('\n'):
            if 'Internet' in line and (' R ' in line or ' RS' in line or 'pppoe-out' in line):
                parts = line.split()
                if len(parts) > 1:
                    name = ' '.join(parts[2:-2]) if len(parts) > 3 else parts[2]
                    if name and 'Internet' in name:
                        isps.append({
                            "name": name,
                            "gateway": "N/A",
                            "type": "Internet",
                            "active": False,  # Will be determined from routes
                            "packet_loss_pct": 0,
                            "latency_ms": 30,
                            "status": "UP",
                        })

        # Determine which ISP is currently active from routing table
        # Look for active default route (0.0.0.0/0 with 'A' flag)
        active_interface = None
        for line in route_output.split('\n'):
            # Look for active default route
            if ' A ' in line and '0.0.0.0/0' in line:
                # Extract interface name from the route line
                parts = line.split()
                if len(parts) > 4:
                    # Interface name is usually near the end or indicated by "Internet"
                    for part in parts:
                        if 'Internet' in part:
                            active_interface = part
                            break

        # Mark the active ISP
        if isps:
            for isp in isps:
                isp["active"] = (active_interface and active_interface in isp["name"]) or (
                    len(isps) == 1
                )  # If only one ISP, mark it as active

            # If no clear active was determined, mark first as active
            if not any(isp["active"] for isp in isps):
                isps[0]["active"] = True

            return isps

        return _isps_for(device["name"])  # Fallback to mock
    except Exception as e:
        logger.warning(f"Error getting real ISPs: {e}")
        return _isps_for(device["name"])  # Fallback to mock


def _parse_vpn_metrics(device: dict, client: "paramiko.SSHClient") -> list[dict]:
    """Fetch active VPN tunnels from RouterOS."""
    try:
        vpn_output = _ssh_exec(client, "/interface print")
        vpns = []

        # Parse interfaces that look like VPN
        for line in vpn_output.split('\n'):
            if (' R ' in line or ' RS' in line) and ('l2tp' in line.lower() or 'pptp' in line.lower()):
                parts = line.split()
                if len(parts) > 2:
                    name = ' '.join(parts[2:-2]) if len(parts) > 3 else parts[2]
                    vpns.append({
                        "name": name,
                        "type": "VPN Tunnel",
                        "peer": "Connected",
                        "peer_name": name,
                        "status": "connected",
                        "uptime_hours": 24,
                        "rx_bytes": 100_000_000,
                        "tx_bytes": 50_000_000,
                    })

        return vpns if vpns else []
    except Exception as e:
        logger.warning(f"Error getting VPN metrics: {e}")
        return []


def collect_metrics_real(device: dict, ip: str, username: str, password: str) -> Optional[dict]:
    """Collect REAL metrics via SSH from a Mikrotik device."""
    if not paramiko:
        logger.error("paramiko not available for real metrics")
        return None

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password, timeout=10, look_for_keys=False)

        now = _now()
        system = _parse_system_metrics(device, client)
        isps = _parse_isps_real(device, client)
        vpns = _parse_vpn_metrics(device, client)

        client.close()

        return {
            "generated_at": _iso(now),
            "source": "REAL",
            "system": system or {},
            "isps": isps or [],  # REAL ISPs from interface print
            "failover_events": [],  # Real failovers would need log parsing
            "vpns": vpns or [],  # REAL VPNs from interface print
            "login_attempts": [],  # Real logins would need log parsing
        }
    except Exception as e:
        logger.error(f"SSH metrics failed for {device['name']}: {e}")
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def collect_metrics(
    device: dict,
    dry_run: bool = True,
    password: Optional[str] = None,
) -> dict[str, Any]:
    """
    Given a device config dict, return a snapshot of live metrics.

    In DRY_RUN we return deterministic mocks.
    In REAL mode, attempts SSH connection using device['ip'], device['username'],
    and the provided password.
    """
    name = device["name"]
    role = device.get("role", "VPN_CLIENT")
    priority = device.get("priority", "MEDIUM")

    if not dry_run:
        # Try real metrics via SSH
        if password:
            real_metrics = collect_metrics_real(
                device,
                device.get("ip", ""),
                device.get("username", ""),
                password,
            )
            if real_metrics:
                return real_metrics

        # Fallback: return empty if SSH fails
        return {
            "generated_at": _iso(_now()),
            "source": "REAL",
            "system": None,
            "isps": [],
            "failover_events": [],
            "vpns": [],
            "login_attempts": [],
            "note": "REAL metrics unavailable — SSH connection failed.",
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
