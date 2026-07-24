# ⚡ TEKOSECURE - LAUNCHER MAESTRO v2.0

## 🎯 INICIO EN 3 PASOS

### Paso 1: Setup Inicial (Primera Vez Solamente)
```bash
# Abre CMD o PowerShell en C:\Users\TI\Desktop\Tekosecure
cd C:\Users\TI\Desktop\Tekosecure
SETUP.bat
```

Esto:
- ✅ Verifica que Python y wrangler están instalados
- ✅ Crea acceso directo `TEKOSECURE.lnk` en Desktop
- ✅ Genera carpeta de logs

### Paso 2: Usar TEKOSECURE (Siempre)
**Simplemente:** Haz doble clic en `TEKOSECURE.lnk` en tu Desktop

El sistema:
- ✅ Inicia Backend (FastAPI) en puerto 8001
- ✅ Inicia Tunnel (Cloudflare) 
- ✅ Abre navegador automáticamente
- ✅ Muestra logs en tiempo real
- ✅ Todo listo en ~30 segundos

### Paso 3: Acceder al Dashboard
Se abre automáticamente en:
```
https://tekosecurity.vercel.app
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
C:\Users\TI\Desktop\Tekosecure\
├── SETUP.bat                      ← Ejecutar UNA VEZ (primera vez)
├── README_LAUNCHER.md             ← Este archivo
├── STARTUP_GUIDE.md               ← Guía completa (opcional)
├── scripts/
│   ├── startup/
│   │   ├── tekosecure-launcher.ps1           ← Script maestro (el motor)
│   │   ├── tekosecure-launcher.vbs           ← Ejecutor con logs visibles
│   │   └── tekosecure-launcher-silent.vbs    ← Ejecutor silencioso (opcional)
│   ├── setup/
│   │   └── create-shortcut.vbs                ← Crea acceso directo
│   └── monitor/
│       └── check-status.ps1                   ← Verifica si está corriendo
├── logs/
│   └── launcher/
│       ├── tekosecure-*.log                  ← Logs maestro
│       ├── backend.log                       ← Logs Backend
│       ├── backend-error.log
│       ├── tunnel.log                        ← Logs Tunnel
│       └── tunnel-error.log
├── backend/
│   ├── server.py                  ← FastAPI (puerto 8001)
│   └── ... (otros módulos)
├── tunnel/
│   └── config.yml                 ← Configuración Cloudflare Tunnel
└── .env                           ← Credenciales (NUNCA compartir)
```

---

## 🚀 EJECUCIÓN RÁPIDA

### Primera Vez
```bash
SETUP.bat
```
Luego verifica que `TEKOSECURE.lnk` aparece en tu Desktop.

### Cada Día
```
Doble clic en TEKOSECURE.lnk
```

---

## 📊 QUÉ HACE EL LAUNCHER

| Paso | Acción | Tiempo | Estado |
|------|--------|--------|--------|
| 1 | Inicia Backend (FastAPI) | 3s | 🟡 Iniciando |
| 2 | Verifica Backend | 10-15s | 🟢 Listo |
| 3 | Inicia Tunnel (Cloudflare) | 3-5s | 🟡 Iniciando |
| 4 | Verifica Tunnel | 10-15s | 🟢 Listo |
| 5 | Abre navegador | Automático | 🟢 Accesible |
| **Total** | **Todo operativo** | **~30s** | **✅ Ready** |

---

## 🔗 ACCESO A SERVICIOS

Una vez iniciado:

| Servicio | URL | Uso |
|----------|-----|-----|
| Frontend | https://tekosecurity.vercel.app | **← Usa esto** |
| Backend (Local) | http://localhost:8001 | Desarrollo |
| Backend (Público) | https://api-tekosecure.nasser.com | Producción |
| Health Check | http://localhost:8001/api/health | Verificación |

---

## 🧪 VERIFICAR QUE FUNCIONA

### Opción 1: Visualizar (Fácil)
```bash
# Si ves esto en PowerShell = TODO OK:
✓ Backend respondiendo correctamente
✓ Tunnel respondiendo correctamente
✓ Navegador abierto en https://tekosecurity.vercel.app
========== TEKOSECURE OPERATIVO ==========
```

### Opción 2: Ejecutar Check Manual
```powershell
# En PowerShell:
.\scripts\monitor\check-status.ps1
```

### Opción 3: Curl desde Terminal
```bash
# Verifica Backend
curl http://localhost:8001/api/health

# Verifica Tunnel (requiere HTTPS)
curl https://api-tekosecure.nasser.com/api/health
```

---

## ⚙️ OPCIONES AVANZADAS

### Ver Logs en Tiempo Real (Ya Abiertos)
La ventana PowerShell muestra todo automáticamente.

### Ejecutar Silencioso (Sin Ventana)
```bash
# En lugar de doble clic en .lnk:
cscript "C:\Users\TI\Desktop\Tekosecure\scripts\startup\tekosecure-launcher-silent.vbs"

# Los logs se guardan en:
C:\Users\TI\Desktop\Tekosecure\logs\launcher\
```

### Detener Servicios
```powershell
# Cierra la ventana PowerShell
# O desde otra ventana PowerShell:
Stop-Process -Name python -Force
Stop-Process -Name wrangler -Force
```

---

## 🆘 PROBLEMAS COMUNES

### "Python no encontrado"
```bash
# Instala Python desde https://python.org
# Asegúrate de marcar "Add Python to PATH"
```

### "Wrangler no encontrado"
```bash
npm install -g @cloudflare/wrangler
```

### "Puerto 8001 en uso"
```powershell
# Encuentra qué proceso lo usa:
netstat -ano | findstr ":8001"

# Mata el proceso (reemplaza 1234 por el PID):
taskkill /PID 1234 /F
```

### El navegador no abre
- Abre manualmente: https://tekosecurity.vercel.app
- El backend está corriendo en background

### Tunnel no conecta
```powershell
# Verifica credenciales:
wrangler tunnel list

# Si es necesario, recrea:
wrangler tunnel create tekosecure
```

---

## 🔐 SEGURIDAD

- ✅ Todas las credenciales en `.env` (NUNCA en git)
- ✅ Backend valida JWT en cada request
- ✅ CORS restringido a dominios autorizados
- ✅ Logs se guardan localmente (no en cloud)
- ✅ Passwords de Mikrotik encriptados

---

## 📋 CHECKLIST DE VERIFICACIÓN

Después de iniciar, verifica:

- [ ] Ventana PowerShell muestra "✓ Backend respondiendo"
- [ ] Ventana PowerShell muestra "✓ Tunnel respondiendo"
- [ ] Navegador se abre automáticamente
- [ ] Dashboard carga en https://tekosecurity.vercel.app
- [ ] Puedes ver Mikrotik y NVR data
- [ ] Ventana PowerShell muestra "TEKOSECURE OPERATIVO"

---

## 🎯 FLUJO COMPLETO

```
                    Haces doble clic en TEKOSECURE.lnk
                              ↓
                    VBScript ejecuta PowerShell
                              ↓
                  Launcher inicia Backend (FastAPI)
                              ↓
                  Launcher verifica Backend (Health Check)
                              ↓
                  Launcher inicia Tunnel (Cloudflare)
                              ↓
                  Launcher verifica Tunnel (Health Check)
                              ↓
                  Launcher abre navegador automáticamente
                              ↓
                   📊 DASHBOARD EN VIVO Y ACTIVO
                   ├─ KPIs en tiempo real
                   ├─ Mapa de Mikrotik
                   ├─ Timeline de eventos
                   ├─ Reportes ejecutivos
                   └─ Bloqueo de IPs maliciosas
```

---

## 📞 INFORMACIÓN ÚTIL

**Directorio del Proyecto:**
```
C:\Users\TI\Desktop\Tekosecure
```

**Archivos de Configuración:**
```
C:\Users\TI\Desktop\Tekosecure\.env
C:\Users\TI\Desktop\Tekosecure\tunnel\config.yml
C:\Users\TI\Desktop\Tekosecure\config\mikrotik_config.json
```

**Logs:**
```
C:\Users\TI\Desktop\Tekosecure\logs\launcher\
```

**Frontend en Vivo:**
```
https://tekosecurity.vercel.app
```

---

## 🌟 ¿LISTO?

1. **Abre CMD/PowerShell**
2. **Ejecuta:** `cd C:\Users\TI\Desktop\Tekosecure && SETUP.bat`
3. **Haz doble clic:** En `TEKOSECURE.lnk` en tu Desktop
4. **¡Disfruta!** Dashboard en https://tekosecurity.vercel.app

---

**TEKOSECURE v2.0 - Launcher Maestro**  
**Un clic, todo automático, seguridad en tiempo real.**  
**Monitoreo de infraestructura de Nasser Cubiertas.**

