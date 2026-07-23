# TEKOSECURE — Product Requirements Doc

## Problem Statement (original)
Dashboard SOC en tiempo real conectado a Supabase para monitoreo de red (Mikrotik) y video-vigilancia (9 NVRs Hikvision), detección de ataques, y acciones automáticas de defensa (bloqueo real de IPs por SSH).

## Architecture
```
Browser (React SOC dashboard)
    │
    ├── Supabase JS  → Auth (email/pass) · Realtime · Reads · close-alert (direct)
    │
    └── FastAPI /api/ → verifies Supabase JWT
           │
           ├── /api/actions/block-ip-real
           │      └── paramiko SSH → 4 Mikrotik (24h drop rules)
           │            └── falls back to logs/audit.log if Supabase RLS blocks
           │
           ├── /api/actions/close-alert (PATCH via user JWT)
           └── /api/actions/audit-log, /blocked-ips
```

**Key components** (`/app/backend`):
- `server.py` — FastAPI v2.0 (~370 lines): endpoints, JWT verify, Supabase-or-local audit
- `config_secure.py` — Fernet-based secrets loader (master key in .env, encrypted password blob)
- `mikrotik_actions.py` — MikrotikActionExecutor + MikrotikActionManager, DRY_RUN mode
- `.env` — SUPABASE_*, TEKOSECURE_MASTER_KEY, MIKROTIK_PASSWORD_ENC, MIKROTIK_DRY_RUN

**Frontend** (`/app/frontend`): CRA + Tailwind + Supabase JS + `sonner` + `lucide-react`.

## Security posture
- **No plaintext credentials in git**: `config/mikrotik_config.json` is sanitized (only IPs, roles, usernames). Passwords live encrypted in `backend/.env` (which is gitignored) using Fernet symmetric encryption.
- **JWT-gated backend**: every action endpoint verifies the Supabase access token via `/auth/v1/user`.
- **Reversible blocks**: `/ip firewall filter add ... timeout=24h` → RouterOS auto-removes.
- **Complete audit trail**: every mutation writes `actions_log` in Supabase (or `backend/logs/audit.log` if RLS blocks).
- **DRY_RUN by default in preview**: the Emergent pod cannot reach the customer LAN, so real actions default to simulated.

## User Choices (from Jan 2026 + Jul 2026)
- Auth: Supabase Auth email/password ("Confirm email" off).
- Backend architecture: FastAPI intermediate layer (JWT verify → SSH to Mikrotik).
- Design: SOC dark + neon.
- MVP Fase 1: dashboard + alerts + NVRs + realtime + close-alert.
- Fase 2 (this iteration): real block-ip on Mikrotik with SSH, audit log, encrypted secrets.

## Implemented Milestones
### 2026-07-20 — Fase 1 (session 1)
- Supabase Auth (login/signup/logout), protected routes
- Dashboard `/` — 4 métricas, alertas realtime, mini-NVRs
- `/alerts` — filtros severidad/estado/search/sort + close
- `/nvrs` — cards agrupadas por sucursal
- Realtime (postgres_changes on `attacks` + `hikvision_events`)
- SOC dark theme (Roboto Mono + Inter + neón)
- Backend FastAPI mínimo con `/api/actions/close-alert` y `/api/actions/block-ip` (simulated)
- Tests: 8/8 backend, 19/19 frontend

### 2026-07-21 — Fase 2 (session 2)
- `POST /api/actions/block-ip-real` con SSH real (paramiko) a 4 Mikrotik → drop rules `timeout=24h`
- Fernet symmetric encryption for Mikrotik SSH password (master key in `backend/.env`)
- Sanitized `config/mikrotik_config.json` (safe to commit)
- CLI tool `scripts/encrypt_mikrotik_secret.py` (--generate-key / --encrypt / --decrypt / --check)
- `MIKROTIK_DRY_RUN` mode (safe testing in preview without LAN access)
- Local fallback `logs/audit.log` when Supabase RLS blocks INSERT
- New endpoints: `/api/actions/audit-log`, `/api/actions/blocked-ips`
- Frontend: `MODE: DRY_RUN` badge in header, "BLOQUEAR IP" button per active alert, confirmation modal
- Tests: 16/16 backend, all data-testids green (frontend)

### 2026-07-21 — Fase 3 (session 2 · bug fix)
- **Bug reportado**: "No veo el apartado de mikrotiks en el sistema, no hay nada"
- New endpoint `GET /api/mikrotiks` — returns sanitized topology (no passwords) + security policy + current mode. JWT required.
- New page `/mikrotiks` (`MikrotiksPage.jsx`) — 4 cards con IP LAN, IP pública, subnet, rol (VPN_SERVER_HUB / VPN_CLIENT), modelo, descripción, prioridad neón (CRITICAL/HIGH), badge HUB, contador BLOQ 24h por sucursal
- New nav entry "MIKROTIKS" con icon `Router` (sidebar desktop + bottom nav mobile)
- Panel "Política de Seguridad Activa" con thresholds y modo
- Tests: 21/21 backend, frontend 100% (incluye test test_mikrotiks_no_password_leak)

### 2026-07-21 — Fase 4 (session 2 · bug fix)
- **Bug reportado**: "/mikrotiks muestra 'SIN GATEWAYS CONFIGURADOS' aunque el backend retorna count=4"
- Root cause: JWT del usuario expirado en background (Supabase autoRefresh no dispara si el tab está inactivo) → backend 403 → UI caía a 'sin gateways' porque no distinguía error de config vacía
- New helper `/app/frontend/src/lib/api.js` — `apiFetch()` con refresh proactivo (SKEW=60s antes de expirar) + retry único en 401/403 + `ApiError` con status/body/url
- `MikrotiksPage.jsx` refactor: distingue estado **error** (`data-testid="mikrotiks-error"` + botón `mikrotiks-retry`) del estado **empty config** (sólo si respuesta OK y lista vacía)
- `BlockIpModal.jsx` migrado también a `apiFetch`
- Tests: 21/21 backend + frontend 100% incluyendo escenario forzado de fallo con `page.route` intercept

### 2026-07-23 — Fase 5 (session 3 · Reports + Deploy package)
- **New module** `/app/backend/reports.py` — aggregates from Supabase `attacks` table: totales por tipo, severidad, status, top 15 IPs, cross-tab tipo×severidad, serie temporal diaria
- **New endpoint** `GET /api/reports/summary?days=30` (JWT) — devuelve el summary JSON
- **New endpoint** `GET /api/reports/export.xlsx?days=30` (JWT via header o `?token_qs=`) — genera Excel con **5 hojas**: Resumen · Tipos por Severidad · Top IPs · Serie temporal · Detalle. Coloreado por severidad, freeze panes en Detalle, filename dinámico
- **New page** `/reports` (`ReportsPage.jsx`) — KPIs neón por severidad, barras horizontales de tipos y top-IPs, matriz cruzada con chips coloreados, serie temporal (bar chart CSS-only), filtros preset (24h/7d/30d/90d) + date-range custom, botón DESCARGAR EXCEL
- **New nav entry** "REPORTES" con icono `FileSpreadsheet`
- **CORS parametrizable**: `CORS_ORIGINS` desde env (default `*` en dev; para producción → `https://tekosecurity.vercel.app`)
- **Paquete de deploy** listo para on-prem híbrido gratis:
  - `/app/frontend/vercel.json` (Create React App preset, rewrites, cache headers)
  - `/app/frontend/.env.production.example`
  - `/app/backend/Dockerfile` + `docker-compose.yml`
  - `/app/backend/start_windows.bat` (venv + uvicorn autoinstall)
  - `/app/README-DEPLOY.md` — guía paso a paso: GitHub → Vercel → Windows/Docker → Cloudflare Tunnel → verificación E2E, endurecimiento, FAQ
- Tests: 28/28 backend (21 regresión + 7 nuevos de reports) + frontend 100%

### 2026-07-23 — Fase 6 (session 3 · mini-Zabbix per-Mikrotik)
- **New module** `/app/backend/mikrotik_metrics.py` — generador determinista de métricas mockeadas (seed = MD5 del device name), stable entre refreshes
- **New endpoint** `GET /api/mikrotiks/{name}` — device + metrics {system, isps, failover_events, vpns, login_attempts}, lookup case-insensitive, 404 en devices no configurados
- **Topología por device**: MATRIZ_KM6/HERNANDARIAS con 2 ISPs, OASIS/KM12 con 1 ISP; HERNANDARIAS mockeado en failover activo hacia ISP2 con 3 eventos recientes; MATRIZ_KM6 hub con 3 túneles L2TP/IPsec (uno a cada cliente)
- **New page** `/mikrotiks/:name` (`MikrotikDetailPage.jsx`):
  - 5 gauges (CPU load · Memoria · Temp · Storage libre · Uptime) con umbrales de color
  - Panel Conectividad · Proveedores: cada ISP con packet loss (bar), latencia, estado UP/DEGRADED, badge ACTIVO/STANDBY
  - Panel Failovers recientes (últimas 12h) con timestamp relativo
  - Panel VPNs activas con peer, uptime, TX/RX bytes
  - Tabla intentos de acceso (SSH/Winbox/WebFig) con OK/FAIL coloreado
  - Auto-refresh 20s toggle + refresh manual
- Cards de `/mikrotiks` ahora son `<Link>` clickeables
- **DRY_RUN placeholder** en REAL mode — SSH real queda como stub para Fase 7 (ejecutar `/system resource print`, `/ip route print`, `/interface print`, `/log print`)
- Tests: 36/36 backend (28 regresión + 8 nuevos) + frontend 100%

## Backlog / Fase 3 (P0 → P2)
- **P0**: [USER ACTION] Rotar password del user `nasserti` en los 4 Mikrotik (la anterior estuvo en GitHub público)
- **P0**: [USER ACTION] Ejecutar `/app/scripts/create_actions_log.sql` en Supabase SQL Editor
- **P0**: Desplegar backend on-prem (Windows en `C:\Users\TI\Desktop\Tekosecure` o Linux server dentro de LAN) para desactivar DRY_RUN
- **P1**: Panel "Historial de Acciones" en el frontend consumiendo `/api/actions/audit-log`
- **P1**: Panel "IPs Bloqueadas Actualmente" con desbloqueo manual
- **P1**: Gráficos estadísticos (Recharts) — attacks por tipo/severidad, timeline 24h
- **P1**: Roles admin/operator/viewer con Supabase RLS
- **P2**: PDF reports mensuales
- **P2**: Push notifications web para alertas CRITICAL
- **P2**: Migrar SSH password → llaves SSH (`/user ssh-keys`) en Mikrotik

## Test credentials
See `/app/memory/test_credentials.md`.

## Files (high-level)
```
/app/backend/
  server.py                 FastAPI v2.0
  mikrotik_actions.py       SSH executor with DRY_RUN
  config_secure.py          Fernet secrets loader
  requirements.txt          + paramiko, cryptography
  .env                      TEKOSECURE_MASTER_KEY, MIKROTIK_PASSWORD_ENC, ...
  .env.example              template
  logs/
    api.log                 uvicorn logs
    audit.log               fallback audit trail
  tests/backend_test.py     16 pytest tests

/app/frontend/src/
  App.js, index.js, index.css
  lib/{supabase, auth, format}.js
  pages/{LoginPage, DashboardLayout, DashboardHome, AlertsPage, NvrPage}.jsx
  components/{AlertRow, MetricCard, NvrCard, BlockIpModal}.jsx

/app/config/mikrotik_config.json     Sanitized topology (safe to commit)
/app/scripts/
  seed_supabase.py                    Idempotent seed
  encrypt_mikrotik_secret.py          Fernet CLI
  create_actions_log.sql              RLS policies to run in Supabase
/app/docs/EMERGENT_APP_BRIEF.md       Original brief
```
