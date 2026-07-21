# TEKOSECURE — Credenciales de prueba

## Supabase Auth (Email + Password)

| Rol | Email | Password |
|---|---|---|
| Admin/Operador (principal) | `ti@nasser.com.py` | `NasserTi73491654` |
| Admin/Operador (backup) | `admin@gmail.com` | `Tekosecure2026!` |

Notas:
- Autenticación con Supabase Auth (proyecto `fsucygjqzskwtnynvgob`, "Confirm email" desactivado).
- Registro adicional desde `/login` → "¿Sin cuenta? Registrar operador →".

## Secrets cifrados (v2.0)

**Master key (Fernet):** vive únicamente en `/app/backend/.env` como `TEKOSECURE_MASTER_KEY`.

**Password Mikrotik cifrado:** `MIKROTIK_PASSWORD_ENC` en `/app/backend/.env`.

**Rotación de credenciales SSH:**
```bash
# Generar nueva master key (opcional, rota TODO)
python3 /app/scripts/encrypt_mikrotik_secret.py --generate-key

# Cifrar nueva password con la key actual
python3 /app/scripts/encrypt_mikrotik_secret.py --encrypt "NUEVA_PASSWORD_MIKROTIK"

# Copiar el blob resultante a backend/.env → MIKROTIK_PASSWORD_ENC
# Reiniciar: sudo supervisorctl restart backend
# Verificar: python3 /app/scripts/encrypt_mikrotik_secret.py --check
```

## Modo operacional

`/app/backend/.env` → `MIKROTIK_DRY_RUN=true` (default en Emergent preview).
- `true` → `/api/actions/block-ip-real` retorna éxito simulado sin abrir SSH.
- `false` → SSH real a los 4 Mikrotik (solo en despliegue on-prem con acceso a la LAN).

## Supabase Project
- URL: https://fsucygjqzskwtnynvgob.supabase.co
- Anon key (public): `sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh`

## Pendiente del usuario
1. **Rotar la password del usuario `nasserti`** en los 4 Mikrotik (la anterior estuvo en GitHub público)
2. Ejecutar `/app/scripts/create_actions_log.sql` en Supabase SQL Editor para habilitar RLS policies en `actions_log`

## Datos seed
- 9 NVRs (8 ONLINE, 1 OFFLINE — Zona Franca Global NVR1)
- 15 attacks (mixed ACTIVE/CLOSED)
- Reseed idempotente: `python3 /app/scripts/seed_supabase.py`
