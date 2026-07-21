"""
TEKOSECURE — Mikrotik Action Executor

Runs real firewall changes on RouterOS devices over SSH (paramiko).

Design:
- Every executor supports a DRY_RUN mode: when enabled it does not open a socket
  and returns synthetic success. This lets us test the full API + audit-log
  pipeline in environments that cannot reach the customer LAN (e.g. the
  Emergent preview pod). On-prem the operator sets MIKROTIK_DRY_RUN=false.
- MikrotikActionManager fan-outs to all devices in parallel-ish (sequential
  loop; connect overhead per host is <1s so this is fine for 4 sites).
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional

import paramiko

logger = logging.getLogger(__name__)


class MikrotikActionExecutor:
    """Executes actions on a single Mikrotik via SSH."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 22,
        dry_run: bool = False,
    ):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.dry_run = dry_run
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self) -> bool:
        if self.dry_run:
            logger.info(f"[DRY_RUN] would connect to {self.host}")
            return True
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=8,
                banner_timeout=8,
                auth_timeout=8,
                allow_agent=False,
                look_for_keys=False,
            )
            logger.info(f"connected to Mikrotik {self.host}")
            return True
        except Exception as exc:
            logger.error(f"cannot connect to {self.host}: {exc}")
            return False

    def disconnect(self):
        if self.dry_run or not self.client:
            return
        try:
            self.client.close()
        except Exception:
            pass

    def _exec(self, command: str) -> Dict[str, str]:
        if self.dry_run:
            return {"status": "success", "output": "(dry-run)", "command": command}
        if not self.client:
            return {"status": "error", "message": "not connected", "command": command}
        try:
            _, stdout, stderr = self.client.exec_command(command, timeout=8)
            out = stdout.read().decode("utf-8", errors="ignore")
            err = stderr.read().decode("utf-8", errors="ignore")
            return {
                "status": "error" if err.strip() else "success",
                "output": out,
                "error": err,
                "command": command,
            }
        except Exception as exc:
            return {"status": "error", "message": str(exc), "command": command}

    def block_ip(
        self,
        source_ip: str,
        reason: str = "TEKOSECURE",
        temporary: bool = True,
    ) -> dict:
        """Drop packets from source_ip on both INPUT and FORWARD chains."""
        # RouterOS: `timeout=` on `/ip firewall filter add` auto-removes the rule.
        timeout_part = " timeout=24h" if temporary else ""
        comment = f'"TEKOSECURE:{reason}"'

        commands = [
            f'/ip firewall filter add chain=input action=drop src-address={source_ip} comment={comment}{timeout_part}',
            f'/ip firewall filter add chain=forward action=drop src-address={source_ip} comment={comment}{timeout_part}',
        ]
        results = [self._exec(cmd) for cmd in commands]
        overall = all(r["status"] == "success" for r in results)
        return {
            "action": "block_ip",
            "host": self.host,
            "ip": source_ip,
            "reason": reason,
            "temporary": temporary,
            "success": overall,
            "results": results,
        }

    def get_blocked_ips(self) -> List[str]:
        result = self._exec('/ip firewall filter print where comment~"TEKOSECURE"')
        if result["status"] != "success":
            return []
        ips: List[str] = []
        for line in (result.get("output") or "").splitlines():
            if "src-address=" in line:
                try:
                    ip = line.split("src-address=")[1].split(" ")[0].strip()
                    if ip:
                        ips.append(ip)
                except IndexError:
                    continue
        return ips


class MikrotikActionManager:
    """Fan-out actions to every configured Mikrotik."""

    def __init__(self, mikrotik_config: Dict[str, dict], dry_run: bool = False):
        """
        mikrotik_config: {"MATRIZ_KM6": {"ip":..., "username":..., "password":...}, ...}
        """
        self.config = mikrotik_config
        self.dry_run = dry_run
        self.clients: Dict[str, MikrotikActionExecutor] = {}
        self.failed_connections: List[str] = []

    def connect_all(self) -> None:
        for name, cfg in self.config.items():
            client = MikrotikActionExecutor(
                host=cfg["ip"],
                username=cfg["username"],
                password=cfg["password"],
                dry_run=self.dry_run,
            )
            if client.connect():
                self.clients[name] = client
            else:
                self.failed_connections.append(name)

    def block_ip_all_locations(
        self,
        source_ip: str,
        reason: str = "TEKOSECURE",
        temporary: bool = True,
    ) -> Dict[str, dict]:
        results: Dict[str, dict] = {}
        for name, client in self.clients.items():
            t0 = time.time()
            res = client.block_ip(source_ip, reason=reason, temporary=temporary)
            res["duration_ms"] = int((time.time() - t0) * 1000)
            results[name] = res
        return results

    def get_all_blocked_ips(self) -> Dict[str, List[str]]:
        return {name: c.get_blocked_ips() for name, c in self.clients.items()}

    def disconnect_all(self) -> None:
        for client in self.clients.values():
            client.disconnect()
