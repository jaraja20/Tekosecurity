"""
TEKOSECURE — FastAPI intermediate layer.

Purpose: expose a minimal API for action endpoints that a browser client
cannot (or should not) perform directly against Supabase (e.g. blocking IPs
via fail2ban, generating PDF reports). The current MVP surface is small on
purpose — Supabase JS is the primary data plane on the frontend.
"""

import os
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv(Path(__file__).parent / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

app = FastAPI(title="TEKOSECURE API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BlockIPRequest(BaseModel):
    attack_id: int
    source_ip: str


class CloseAlertRequest(BaseModel):
    attack_id: int


async def _verify_supabase_token(access_token: str) -> dict:
    """Validates a Supabase JWT by asking Supabase for the user."""
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


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "tekosecure-api"}


@app.get("/api/me")
async def me(authorization: Optional[str] = Header(default=None)):
    token = (authorization or "").replace("Bearer ", "").strip()
    return await _verify_supabase_token(token)


@app.post("/api/actions/block-ip")
async def block_ip(
    payload: BlockIPRequest,
    authorization: Optional[str] = Header(default=None),
):
    """Placeholder for Phase 2 — will invoke fail2ban on the Mikrotik host."""
    token = (authorization or "").replace("Bearer ", "").strip()
    user = await _verify_supabase_token(token)
    # Phase 2: run fail2ban-client set sshd banip <source_ip>
    return {
        "success": True,
        "message": f"IP {payload.source_ip} queued for block (simulated)",
        "attack_id": payload.attack_id,
        "actor": user.get("email"),
    }


@app.post("/api/actions/close-alert")
async def close_alert(
    payload: CloseAlertRequest,
    authorization: Optional[str] = Header(default=None),
):
    token = (authorization or "").replace("Bearer ", "").strip()
    await _verify_supabase_token(token)
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
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return {"success": True, "data": r.json()}
