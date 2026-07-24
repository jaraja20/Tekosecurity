"""
TEKOSECURE — FastAPI intermediate layer (v2 — REAL ACTIONS)

Endpoints:
    GET  /api/health                    → liveness + mode
    GET  /api/me                        → current Supabase user (JWT required)
    POST /api/actions/close-alert       → mark attack as CLOSED (JWT)
    POST /api/actions/block-ip          → legacy simulated (kept for compat)
    POST /api/actions/block-ip-real     → real SSH block on the 4 Mikrotiks
                                          (respects MIKROTIK_DRY_RUN)
    GET  /api/actions/blocked-ips       → currently blocked IPs (attacks table)
    GET  /api/actions/audit-log         → last 100 entries from actions_log

Every mutation writes to Supabase table `actions_log` (see
scripts/create_actions_log.sql). If the table is missing OR the write fails,
we fall back to a local file `logs/audit.log` so nothing is ever lost.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Add backend to path so we can import modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend import security  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parent
LOG_DIR = BACKEND_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BACKEND_DIR.parent / ".env")

# --- Logging (safe: dir is created above) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "api.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("tekosecure")

# Import local modules
sys.path.insert(0, str(BACKEND_DIR))
from backend.config_secure import (  # noqa: E402
    SecretsError,
    as_connection_map,
    is_dry_run,
    load_mikrotik_config,
)
from backend.mikrotik_actions import MikrotikActionManager  # noqa: E402
from backend import mikrotik_metrics  # noqa: E402
from backend import reports  # noqa: E402

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # optional

# CORS: RESTRINGIDO SOLO A DOMINIOS PERMITIDOS
CORS_ORIGINS = security.ALLOWED_ORIGINS

app = FastAPI(title="TEKOSECURE API", version="2.0.0")

# Security Middleware - Orden importante
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "tekosecurity.vercel.app", "api-tekosecure.localhost.run", "*.loca.lt"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Métodos específicos
    allow_headers=["Authorization", "Content-Type", "bypass-tunnel-reminder"],  # Headers específicos
)

# Middleware para security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    for header, value in security.SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class BlockIPRequest(BaseModel):
    attack_id: int
    source_ip: str
    reason: Optional[str] = "TEKOSECURE Attack"


class CloseAlertRequest(BaseModel):
    attack_id: int


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
async def _verify_supabase_token(access_token: str) -> dict:
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing token")
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {access_token}",
            },
        )
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")
    return r.json()


def _bearer(authorization: Optional[str]) -> str:
    return (authorization or "").replace("Bearer ", "").strip()


# ---------------------------------------------------------------------------
# Audit log — Supabase + local fallback
# ---------------------------------------------------------------------------
AUDIT_FILE = LOG_DIR / "audit.log"


def _audit_local(entry: dict) -> None:
    try:
        with AUDIT_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")
    except OSError as exc:
        logger.error(f"cannot write local audit log: {exc}")


async def _audit(
    actor: str,
    action: str,
    target_ip: str,
    attack_id: Optional[int],
    status: str,
    details: Optional[dict] = None,
    user_token: Optional[str] = None,
) -> None:
    entry = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "target_ip": target_ip,
        "attack_id": attack_id,
        "status": status,
        "details": details,
    }
    # 1) Try Supabase (with service key if available, else user JWT)
    auth_key = SUPABASE_SERVICE_KEY or user_token or SUPABASE_ANON_KEY
    try:
        async with httpx.AsyncClient(timeout=6) as client:
            r = await client.post(
                f"{SUPABASE_URL}/rest/v1/actions_log",
                headers={
                    "apikey": SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {auth_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                json={**entry, "details": json.dumps(details) if details else None},
            )
        if r.status_code >= 400:
            logger.warning(f"audit → supabase {r.status_code}: {r.text[:160]}")
            _audit_local(entry)
        else:
            logger.info(f"audit ok: {action} target={target_ip} by={actor}")
    except Exception as exc:
        logger.warning(f"audit supabase exception: {exc}")
        _audit_local(entry)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "tekosecure-api",
        "version": "2.0.0",
        "mode": "DRY_RUN" if is_dry_run() else "REAL_ACTIONS",
    }


@app.get("/api/me")
async def me(authorization: Optional[str] = Header(default=None)):
    return await _verify_supabase_token(_bearer(authorization))


@app.get("/api/mikrotiks")
async def list_mikrotiks(authorization: Optional[str] = Header(default=None)):
    """Return the sanitized Mikrotik topology (NO passwords) + current mode."""
    try:
        logger.info(f"GET /api/mikrotiks - verifying token...")
        await _verify_supabase_token(_bearer(authorization))
        logger.info(f"Token verified, loading config...")
        cfg = load_mikrotik_config()
        logger.info(f"Config loaded, building response...")

        devices = []
        for mk in cfg.get("mikrotiks", []):
            # Explicitly strip password from response
            safe = {k: v for k, v in mk.items() if k != "password"}
            devices.append(safe)

        logger.info(f"Returning {len(devices)} devices")
        return {
            "mode": "DRY_RUN" if is_dry_run() else "REAL_ACTIONS",
            "count": len(devices),
            "mikrotiks": devices,
            "security_policy": cfg.get("security_policy", {}),
        }
    except Exception as e:
        logger.error(f"ERROR in list_mikrotiks: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mikrotiks/{name}")
async def get_mikrotik_detail(
    name: str,
    authorization: Optional[str] = Header(default=None),
):
    """Detail view of a single Mikrotik + live metrics (real via SSH or mocked)."""
    await _verify_supabase_token(_bearer(authorization))
    try:
        cfg = load_mikrotik_config()
    except SecretsError as exc:
        raise HTTPException(status_code=500, detail=f"Config error: {exc}")

    device = next(
        (m for m in cfg.get("mikrotiks", []) if m["name"].upper() == name.upper()),
        None,
    )
    if device is None:
        raise HTTPException(status_code=404, detail=f"Mikrotik '{name}' not found")

    safe = {k: v for k, v in device.items() if k != "password"}
    # Pass password to collect_metrics if REAL mode (not dry_run)
    metrics = mikrotik_metrics.collect_metrics(
        safe,
        dry_run=is_dry_run(),
        password=device.get("password") if not is_dry_run() else None,
    )
    return {
        "device": safe,
        "mode": "DRY_RUN" if is_dry_run() else "REAL_ACTIONS",
        "metrics": metrics,
    }


@app.get("/api/mikrotiks/{name}/metrics-stream")
async def metrics_stream(
    name: str,
    authorization: Optional[str] = Header(default=None),
):
    """Server-Sent Events stream for real-time metrics. Sends updates every 3 seconds."""
    import asyncio

    await _verify_supabase_token(_bearer(authorization))

    async def event_generator():
        try:
            cfg = load_mikrotik_config()
            device = next(
                (m for m in cfg.get("mikrotiks", []) if m["name"].upper() == name.upper()),
                None,
            )
            if device is None:
                yield f"data: {json.dumps({'error': 'Device not found'})}\n\n"
                return

            # Stream metrics every 3 seconds
            while True:
                try:
                    safe = {k: v for k, v in device.items() if k != "password"}
                    metrics = mikrotik_metrics.collect_metrics(
                        safe,
                        dry_run=is_dry_run(),
                        password=device.get("password") if not is_dry_run() else None,
                    )

                    # Send SSE event
                    yield f"data: {json.dumps(metrics)}\n\n"

                    # Wait 3 seconds before next update
                    await asyncio.sleep(3)
                except Exception as e:
                    logger.error(f"Error in metrics stream: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    break
        except Exception as e:
            logger.error(f"Stream error for {name}: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/actions/close-alert")
async def close_alert(
    payload: CloseAlertRequest,
    authorization: Optional[str] = Header(default=None),
):
    token = _bearer(authorization)
    user = await _verify_supabase_token(token)
    actor = user.get("email", "unknown")

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.patch(
            f"{SUPABASE_URL}/rest/v1/attacks",
            params={"id": f"eq.{payload.attack_id}"},
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            json={"status": "CLOSED"},
        )
    if r.status_code >= 400:
        await _audit(actor, "CLOSE_ALERT_FAILED", "N/A", payload.attack_id, "FAILED",
                     {"http": r.status_code, "body": r.text[:200]}, token)
        raise HTTPException(status_code=r.status_code, detail=r.text)

    await _audit(actor, "CLOSE_ALERT", "N/A", payload.attack_id, "SUCCESS", None, token)
    return {"success": True, "attack_id": payload.attack_id, "actor": actor, "data": r.json()}


@app.post("/api/actions/block-ip")
async def block_ip_legacy(
    payload: BlockIPRequest,
    authorization: Optional[str] = Header(default=None),
):
    """Legacy simulated endpoint. Kept so existing UI/tests don't break."""
    token = _bearer(authorization)
    user = await _verify_supabase_token(token)
    actor = user.get("email", "unknown")
    await _audit(actor, "BLOCK_IP_SIMULATED", payload.source_ip, payload.attack_id,
                 "SUCCESS", {"note": "legacy simulated endpoint"}, token)
    return {
        "success": True,
        "message": f"IP {payload.source_ip} queued for block (simulated)",
        "attack_id": payload.attack_id,
        "actor": actor,
    }


@app.post("/api/actions/block-ip-real")
async def block_ip_real(
    payload: BlockIPRequest,
    authorization: Optional[str] = Header(default=None),
):
    """
    Bloqueo REAL: se conecta por SSH a los Mikrotik y añade drop rules
    con timeout=24h. Cuando MIKROTIK_DRY_RUN=true no toca la red y devuelve
    éxito simulado (para el preview en Emergent).
    """
    token = _bearer(authorization)
    user = await _verify_supabase_token(token)
    actor = user.get("email", "unknown")

    dry = is_dry_run()
    logger.info(f"BLOCK_IP_REAL {payload.source_ip} by {actor} dry_run={dry}")

    manager: Optional[MikrotikActionManager] = None
    try:
        conn_map = as_connection_map(load_mikrotik_config())
        manager = MikrotikActionManager(conn_map, dry_run=dry)
        manager.connect_all()

        if not manager.clients:
            raise RuntimeError(
                f"Could not connect to any Mikrotik. Failed: {manager.failed_connections}"
            )

        results = manager.block_ip_all_locations(
            source_ip=payload.source_ip,
            reason=f"attack#{payload.attack_id}:{payload.reason}",
            temporary=True,
        )

        successful = [n for n, r in results.items() if r.get("success")]
        failed = [n for n, r in results.items() if not r.get("success")]

        await _audit(
            actor,
            "BLOCK_IP_REAL",
            payload.source_ip,
            payload.attack_id,
            "SUCCESS" if successful and not failed else ("PARTIAL" if successful else "FAILED"),
            {
                "dry_run": dry,
                "successful": successful,
                "failed": failed,
                "unreachable": manager.failed_connections,
                "expires_in_hours": 24,
            },
            token,
        )

        return {
            "success": bool(successful),
            "message": (
                f"IP {payload.source_ip} bloqueada en {len(successful)} sucursal(es) "
                f"por 24h {'(DRY-RUN)' if dry else ''}"
            ).strip(),
            "attack_id": payload.attack_id,
            "actor": actor,
            "mode": "DRY_RUN" if dry else "REAL",
            "locations_blocked": successful,
            "locations_failed": failed,
            "locations_unreachable": manager.failed_connections,
            "expires_in_hours": 24,
        }

    except SecretsError as exc:
        logger.error(f"secrets error: {exc}")
        await _audit(actor, "BLOCK_IP_REAL_FAILED", payload.source_ip, payload.attack_id,
                     "FAILED", {"error": "secrets_missing", "detail": str(exc)}, token)
        raise HTTPException(status_code=500, detail=f"Config error: {exc}")

    except Exception as exc:
        logger.error(f"block-ip-real failed: {exc}")
        await _audit(actor, "BLOCK_IP_REAL_FAILED", payload.source_ip, payload.attack_id,
                     "FAILED", {"error": str(exc)}, token)
        raise HTTPException(status_code=500, detail=str(exc))

    finally:
        if manager is not None:
            manager.disconnect_all()


@app.get("/api/actions/blocked-ips")
async def get_blocked_ips(authorization: Optional[str] = Header(default=None)):
    token = _bearer(authorization)
    await _verify_supabase_token(token)
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/actions_log",
            params={
                "select": "target_ip,action,status,created_at,actor,attack_id",
                "action": "eq.BLOCK_IP_REAL",
                "order": "created_at.desc",
                "limit": "100",
            },
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}",
            },
        )
    if r.status_code >= 400:
        # table may not exist yet
        return {"success": False, "blocked": [], "error": r.text[:200]}
    return {"success": True, "blocked": r.json()}


@app.get("/api/actions/audit-log")
async def get_audit_log(
    limit: int = 50,
    authorization: Optional[str] = Header(default=None),
):
    token = _bearer(authorization)
    await _verify_supabase_token(token)
    limit = max(1, min(500, limit))
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/actions_log",
            params={
                "select": "*",
                "order": "created_at.desc",
                "limit": str(limit),
            },
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}",
            },
        )
    if r.status_code >= 400:
        return {"success": False, "entries": [], "error": r.text[:200]}
    return {"success": True, "entries": r.json()}


# ---------------------------------------------------------------------------
# Reports (aggregated stats + xlsx export)
# ---------------------------------------------------------------------------
@app.get("/api/reports/summary")
async def reports_summary(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    days: int = 30,
    authorization: Optional[str] = Header(default=None),
):
    """Aggregated attack stats — used to render the reports page."""
    token = _bearer(authorization)
    await _verify_supabase_token(token)

    if not date_from and not date_to:
        date_from, date_to = reports.default_range(days=max(1, min(days, 365)))

    try:
        attacks = await reports.fetch_attacks(token, date_from, date_to, limit=2000)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    summary = reports.build_summary(attacks)
    return {
        "success": True,
        "range": {"from": date_from, "to": date_to},
        "summary": summary,
    }


@app.get("/api/reports/export.xlsx")
async def reports_export_xlsx(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    days: int = 30,
    authorization: Optional[str] = Header(default=None),
    token_qs: Optional[str] = None,
):
    """
    Streams an Excel workbook with 5 sheets:
      Resumen · Tipos por Severidad · Top IPs · Serie temporal · Detalle

    Accepts the JWT either via Authorization header (normal) OR as ?token_qs=
    query param (needed because <a download> anchors can't set headers).
    """
    token = _bearer(authorization) or (token_qs or "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    await _verify_supabase_token(token)

    if not date_from and not date_to:
        date_from, date_to = reports.default_range(days=max(1, min(days, 365)))

    try:
        attacks = await reports.fetch_attacks(token, date_from, date_to, limit=5000)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    summary = reports.build_summary(attacks)
    xlsx_bytes = reports.build_xlsx(attacks, summary, date_from, date_to)
    filename = reports.suggested_filename(date_from, date_to)

    return StreamingResponse(
        iter([xlsx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(xlsx_bytes)),
        },
    )
