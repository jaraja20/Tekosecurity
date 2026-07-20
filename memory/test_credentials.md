# TEKOSECURE — Credenciales de prueba

## Supabase Auth (Email + Password)

| Rol | Email | Password |
|---|---|---|
| Admin/Operador | `admin@gmail.com` | `Tekosecure2026!` |

Notas:
- Autenticación implementada con Supabase Auth (`@supabase/supabase-js`).
- El proyecto Supabase (`fsucygjqzskwtnynvgob`) tiene "Confirm email" desactivado, por lo que los signups quedan activos de inmediato.
- Para crear nuevos usuarios desde la UI: `/login` → "¿Sin cuenta? Registrar operador →".

## Supabase Project
- URL: https://fsucygjqzskwtnynvgob.supabase.co
- Anon key (public): `sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh`

## Datos seed
- 9 NVRs (8 ONLINE, 1 OFFLINE — Zona Franca Global NVR1)
- 15 attacks (6 ACTIVE, 9 CLOSED)
- Reseed idempotente: `python3 /app/scripts/seed_supabase.py`
