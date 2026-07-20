# TEKOSECURE — Product Requirements Doc

## Problem Statement (original)
Dashboard interactivo en tiempo real para monitoreo de infraestructura de red y video-vigilancia:
- Mikrotik (gateway, ancho de banda, conexiones)
- Hikvision (9 NVRs distribuidos en 5 sucursales)
- Detección de ataques (BRUTE_FORCE, DDoS, PORT_SCAN, ANOMALOUS_TRAFFIC)
- Alertas en tiempo real (Supabase Realtime)

## User Choices (Jan 2026)
- **Arquitectura**: Frontend directo a Supabase (lectura + realtime + auth); FastAPI como capa intermedia para acciones destructivas (Phase 2: fail2ban, PDFs).
- **Auth**: Supabase Auth (email/password) — proyecto `fsucygjqzskwtnynvgob`, "Confirm email" desactivado para demo.
- **MVP Fase 1**: Login, dashboard (3+ métricas), alertas + cerrar, NVRs por sucursal, realtime, responsive.
- **Fase 2 / backlog**: PDF reports, gráficos avanzados, bloquear IP (fail2ban), búsqueda full-text.
- **Diseño**: SOC dark + neón (bg #0a0e27, accents #ff1744/#ff9100/#ffeb3b/#4ade80/#00ff88/#00bfff), Roboto Mono + Inter.

## Architecture
- **Frontend** (`/app/frontend`, CRA + Tailwind, port 3000): React 18, `@supabase/supabase-js` para auth/realtime/queries, `react-router-dom`, `sonner`, `lucide-react`.
- **Backend** (`/app/backend`, FastAPI, port 8001): endpoints mínimos (`/api/health`, `/api/me`, `/api/actions/close-alert`, `/api/actions/block-ip` — el último es MOCKED para Phase 2).
- **DB**: Supabase PostgreSQL remoto — tablas: `attacks`, `hikvision_events`, `network_events`, `alerts_log`, `devices_status`, `users`.
- **Realtime**: `postgres_changes` en `attacks` (INSERT/UPDATE) y `hikvision_events` (INSERT).
- **Seed**: `/app/scripts/seed_supabase.py` idempotente (9 NVRs + 15 attacks mixed).

## User Personas
- **Admin/Operador**: monitorea 24/7, cierra alertas, verifica estado de NVRs.
- **Viewer** (futuro): solo lectura.

## Implemented (2026-07-20)
- [x] Supabase Auth (login/signup/logout) con protección de rutas.
- [x] Dashboard `/`: 4 métricas (alertas activas, NVRs online/total, ataques hoy, stream status), lista live de alertas activas, mini-lista de NVRs.
- [x] Página `/alerts`: tabla completa con filtros por severidad, estado (activas/todas), búsqueda local, sort (recientes/severidad), cerrar alerta.
- [x] Página `/nvrs`: cards agrupadas por sucursal, badge ON/OFF con neón, refresh.
- [x] Realtime end-to-end (INSERT/UPDATE en `attacks` refresca la UI + toast + pulso sonoro).
- [x] SOC dark theme completo (Roboto Mono / Inter, neón, glow, animaciones).
- [x] Responsive (bottom-nav en móvil, layouts adaptativos).
- [x] Backend FastAPI con verificación de JWT vía Supabase `/auth/v1/user`.
- [x] Tests: backend 8/8, frontend 19/19 (Playwright).

## Backlog / Phase 2
- [ ] Gráficos de estadísticas (Recharts): ataques por tipo/severidad, timeline 24h, uptime NVRs 30d.
- [ ] PDF reports mensuales.
- [ ] Bloquear IP real (fail2ban via SSH al Mikrotik host).
- [ ] Búsqueda full-text server-side (Supabase RPC / to_tsvector).
- [ ] Roles: admin / operator / viewer con RLS de Supabase.
- [ ] Sistema de notificaciones sonoras configurables + push web.
- [ ] Historial de acciones (audit log en `alerts_log`).

## Files (high-level)
```
/app/backend/
  server.py            FastAPI intermediate layer
  requirements.txt
  .env                 SUPABASE_URL, SUPABASE_ANON_KEY, MONGO_URL/DB_NAME (unused)
  tests/backend_test.py

/app/frontend/
  package.json
  craco.config.js, tailwind.config.js
  .env                 REACT_APP_SUPABASE_URL, REACT_APP_SUPABASE_ANON_KEY, REACT_APP_BACKEND_URL
  src/
    App.js
    lib/{supabase.js, auth.jsx, format.js}
    pages/{LoginPage, DashboardLayout, DashboardHome, AlertsPage, NvrPage}.jsx
    components/{AlertRow, MetricCard, NvrCard}.jsx

/app/scripts/seed_supabase.py   Idempotent seeder
/app/docs/EMERGENT_APP_BRIEF.md Original brief
```

## Test Credentials
See `/app/memory/test_credentials.md`.
