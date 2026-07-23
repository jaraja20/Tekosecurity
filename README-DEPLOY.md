# TEKOSECURE — Guía de despliegue (Vercel + On-Prem + Supabase, todo gratis)

Arquitectura final:

```
   Navegador
      │
      ▼
   Vercel (Frontend, Free)  ────►  Supabase (Auth · DB · Realtime, Free)
      │
      │  HTTPS  (Cloudflare Tunnel · Free)
      ▼
   Backend FastAPI on-prem  ────►  SSH · Mikrotik LAN (192.168.x.x)
   (Windows Server / Docker)
```

Costo mensual en la nube: **US$ 0** (sólo la electricidad del servidor on-prem).

---

## 1) Prerrequisitos

| # | Herramienta | Dónde obtenerla |
|---|---|---|
| 1 | Cuenta GitHub | https://github.com |
| 2 | Cuenta Vercel | https://vercel.com — login con GitHub |
| 3 | Cuenta Cloudflare (dominio opcional) | https://cloudflare.com |
| 4 | Windows Server / PC 24/7 en la LAN | Ya tienes: `C:\Users\TI\Desktop\Tekosecure` |
| 5 | Python 3.11+ instalado | https://www.python.org/downloads/ |

---

## 2) Subir el código a GitHub

En el chat de Emergent hay un botón **"Save to GitHub"**:
1. Click → crea repo (`Tekosecurity` o el que ya tengas)
2. Push automático de `/app` completo
3. Verifica en GitHub que aparezca `frontend/`, `backend/`, `config/`, `scripts/`

⚠️ **NUNCA subas `backend/.env` a Git** — ya está en `.gitignore`. Si por accidente lo subiste, rota `TEKOSECURE_MASTER_KEY` y `MIKROTIK_PASSWORD_ENC` de inmediato con `scripts/encrypt_mikrotik_secret.py`.

---

## 3) Desplegar el frontend en Vercel

1. Ve a https://vercel.com/new
2. **Import Git Repository** → seleccioná `Tekosecurity`
3. **Configure Project**:
   - Framework Preset: **Create React App** (auto-detect)
   - Root Directory: `frontend`
   - Build Command: `yarn build` (ya en `vercel.json`)
   - Output Directory: `build`
4. **Environment Variables** (Vercel → Settings → Environment Variables):

   ```
   REACT_APP_BACKEND_URL       = https://api.tekosecure.tu-dominio.com
   REACT_APP_SUPABASE_URL      = https://fsucygjqzskwtnynvgob.supabase.co
   REACT_APP_SUPABASE_ANON_KEY = sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh
   ```

   > `REACT_APP_BACKEND_URL` lo llenamos en el paso 5 después de armar el túnel.

5. **Deploy** → en 2 min tenés `https://tekosecurity.vercel.app`.

---

## 4) Instalar el backend en tu Windows

Opción **A — Python directo** (más simple):

```powershell
cd C:\Users\TI\Desktop\Tekosecure\backend
copy .env.example .env
notepad .env       # completá los valores (ver 4.1 más abajo)
start_windows.bat  # instala venv + arranca uvicorn en :8000
```

Opción **B — Docker Desktop**:

```powershell
cd C:\Users\TI\Desktop\Tekosecure\backend
docker compose up -d --build
docker logs -f tekosecure-backend
```

### 4.1) Contenido crítico de `backend/.env`

```dotenv
# Supabase
SUPABASE_URL=https://fsucygjqzskwtnynvgob.supabase.co
SUPABASE_ANON_KEY=sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh

# Cifrado Mikrotik (obtené uno nuevo si el actual estuvo expuesto)
TEKOSECURE_MASTER_KEY=WxajFOOWiI3-IC0aAyoLOpbXgffzy1KV9bHM6fBLJoU=
MIKROTIK_PASSWORD_ENC=gAAAAABqX8dk...............

# ¡IMPORTANTE! Ponelo en FALSE en producción para que el SSH sea real
MIKROTIK_DRY_RUN=false

# Restringir CORS al dominio real (evita que otras webs consuman tu backend)
CORS_ORIGINS=https://tekosecurity.vercel.app
```

Reiniciá el backend después de cambiar `.env`.

**Rotar la contraseña Mikrotik** (recomendado — la anterior estuvo en el repo público):

```powershell
cd backend
python scripts\encrypt_mikrotik_secret.py --encrypt "NUEVA_PASSWORD_MIKROTIK"
# copiá el blob resultante a MIKROTIK_PASSWORD_ENC en .env
python scripts\encrypt_mikrotik_secret.py --check
```

Verificá que funciona: http://localhost:8000/api/health → `{"mode":"REAL_ACTIONS"}`.

---

## 5) Exponer el backend con HTTPS (Cloudflare Tunnel — gratis)

Cloudflare Tunnel te da una URL pública HTTPS gratis, sin abrir puertos en el router.

### 5.1) Instalar `cloudflared` (una sola vez)

- Windows: descargá `cloudflared-windows-amd64.exe` desde
  https://github.com/cloudflare/cloudflared/releases/latest y renombralo a `cloudflared.exe`.
- Poné el ejecutable en `C:\cloudflared\`.

### 5.2) Autenticar

```powershell
cd C:\cloudflared
cloudflared tunnel login
```

Se abre el navegador → autorizás tu dominio en Cloudflare. Si aún no tenés un dominio, comprá uno barato en Cloudflare Registrar (~US$8/año en `.com`).

### 5.3) Crear el túnel y ruta DNS

```powershell
cloudflared tunnel create tekosecure
cloudflared tunnel route dns tekosecure api.tekosecure.tu-dominio.com
```

### 5.4) Configuración del túnel

Creá `C:\Users\TI\.cloudflared\config.yml`:

```yaml
tunnel: tekosecure
credentials-file: C:\Users\TI\.cloudflared\<UUID>.json

ingress:
  - hostname: api.tekosecure.tu-dominio.com
    service: http://localhost:8000
  - service: http_status:404
```

### 5.5) Ejecutar el túnel como servicio de Windows

```powershell
cloudflared service install
# Se instala como servicio; se autoinicia al reiniciar Windows.
```

Verificación: https://api.tekosecure.tu-dominio.com/api/health debería devolver `{"status":"ok","mode":"REAL_ACTIONS"}`.

### 5.6) Volver a Vercel y actualizar la variable

Vercel → Project → Settings → Environment Variables:
- `REACT_APP_BACKEND_URL` = `https://api.tekosecure.tu-dominio.com`

Vercel → Deployments → **Redeploy**.

---

## 6) Alternativa rápida sin dominio: ngrok

Si no querés comprar dominio todavía, usá **ngrok** (gratis, URL aleatoria):

```powershell
# https://ngrok.com/download
ngrok http 8000
# Copiá la URL https://xxxx-xxx.ngrok-free.app y ponela en REACT_APP_BACKEND_URL
```

Limitaciones ngrok free: URL cambia cada vez que reinicias, tráfico limitado.

---

## 7) Endurecimiento post-deploy

- [ ] `MIKROTIK_DRY_RUN=false` en on-prem `.env`
- [ ] `CORS_ORIGINS` restringido a tu dominio Vercel (no `*`)
- [ ] Rotar `nasserti` password en los 4 Mikrotik + re-cifrar con `encrypt_mikrotik_secret.py`
- [ ] Ejecutar `/app/scripts/create_actions_log.sql` en Supabase SQL Editor
- [ ] Confirmar que `backend/.env` NUNCA fue commiteado
- [ ] Habilitar 2FA en GitHub y Vercel
- [ ] En Mikrotik: crear un user SSH dedicado (`tekosecure-agent`) con permisos SÓLO para `/ip firewall filter` y `/log` (principio de mínimo privilegio)

---

## 8) Verificación end-to-end

1. Abrí `https://tekosecurity.vercel.app`
2. Login con `ti@nasser.com.py`
3. Header debe mostrar `MODE: REAL_ACTIONS` (verde neón)
4. En una alerta activa → click **BLOQUEAR IP** → confirmar
5. En el Mikrotik: `/ip firewall filter print where comment~"TEKOSECURE"` → debe aparecer el drop temporal
6. `/reports` → **DESCARGAR EXCEL** → abre en Excel con las 5 hojas

Si algo falla:
- Backend logs: `C:\Users\TI\Desktop\Tekosecure\backend\logs\api.log`
- Audit log: `C:\Users\TI\Desktop\Tekosecure\backend\logs\audit.log`
- Túnel: `cloudflared tunnel info tekosecure`
- Vercel: pestaña "Deployments" → "Logs"

---

## 9) FAQ

**¿Puedo desplegar el backend en la nube (Vercel/Railway) en vez de on-prem?**
No, porque `/api/actions/block-ip-real` hace SSH a IPs privadas (192.168.x.x). Sólo un servidor dentro de tu LAN puede alcanzarlas.

**¿Qué pasa si mi Windows on-prem se apaga?**
El frontend en Vercel sigue vivo (lectura vía Supabase directo). Sólo dejan de funcionar los bloqueos reales y los reports (que van por el backend). El realtime de alertas sigue funcionando porque va Supabase↔navegador.

**¿Cómo actualizo el frontend?**
`git push` a `main` → Vercel autodespliega en 2 min.

**¿Cómo actualizo el backend?**
En el Windows: `git pull` + `start_windows.bat` (o `docker compose pull && docker compose up -d --build`).
