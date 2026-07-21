"""
TEKOSECURE — secure config loader

Loads Mikrotik connection info by combining:
  • config/mikrotik_config.json     → NON-SECRET data (name, ip, location, role...)
                                       Safe to commit to git.
  • backend/.env → TEKOSECURE_MASTER_KEY   → Fernet key for symmetric decryption
                    MIKROTIK_PASSWORD_ENC  → encrypted shared SSH password

If you need per-device passwords in the future, add
MIKROTIK_PASSWORD_ENC_<NAME> variables and this loader will honour them.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


class SecretsError(RuntimeError):
    """Raised when required secrets are missing or invalid."""


def _fernet() -> Fernet:
    key = os.environ.get("TEKOSECURE_MASTER_KEY")
    if not key:
        raise SecretsError(
            "TEKOSECURE_MASTER_KEY not set. Add it to backend/.env "
            "(generate with `python3 /app/scripts/encrypt_mikrotik_secret.py --generate-key`)."
        )
    try:
        return Fernet(key.encode())
    except Exception as exc:
        raise SecretsError(f"Invalid TEKOSECURE_MASTER_KEY: {exc}") from exc


def decrypt(blob: str) -> str:
    try:
        return _fernet().decrypt(blob.encode()).decode()
    except InvalidToken as exc:
        raise SecretsError(
            "Cannot decrypt Mikrotik secret — MASTER_KEY / ENC blob mismatch."
        ) from exc


def encrypt(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def _password_for(name: str) -> Optional[str]:
    # per-device override wins if present
    per_dev = os.environ.get(f"MIKROTIK_PASSWORD_ENC_{name.upper()}")
    if per_dev:
        return decrypt(per_dev)
    shared = os.environ.get("MIKROTIK_PASSWORD_ENC")
    if shared:
        return decrypt(shared)
    return None


def load_mikrotik_config(path: Optional[Path] = None) -> dict:
    """
    Returns:
        {
            "mikrotiks": [
                {"name": "MATRIZ_KM6", "ip": "192.168.13.100",
                 "username": "nasserti", "password": "<plaintext>", ...},
                ...
            ],
            "security_policy": {...}
        }

    Raises SecretsError if a device has no resolvable password.
    """
    cfg_path = path or Path(__file__).resolve().parent.parent / "config" / "mikrotik_config.json"
    with open(cfg_path, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)

    resolved = []
    for mk in cfg.get("mikrotiks", []):
        name = mk["name"]
        password = _password_for(name)
        if not password:
            raise SecretsError(
                f"No encrypted password for {name}. "
                f"Set MIKROTIK_PASSWORD_ENC or MIKROTIK_PASSWORD_ENC_{name.upper()} in backend/.env."
            )
        resolved.append({**mk, "password": password})

    return {**cfg, "mikrotiks": resolved}


def as_connection_map(cfg: Optional[dict] = None) -> dict:
    """
    Return a dict shape MikrotikActionManager expects:
        {"MATRIZ_KM6": {"ip":..., "username":..., "password":...}, ...}
    """
    cfg = cfg or load_mikrotik_config()
    return {
        mk["name"]: {
            "ip": mk["ip"],
            "username": mk["username"],
            "password": mk["password"],
        }
        for mk in cfg["mikrotiks"]
    }


def is_dry_run() -> bool:
    return os.environ.get("MIKROTIK_DRY_RUN", "true").lower() in ("1", "true", "yes")
