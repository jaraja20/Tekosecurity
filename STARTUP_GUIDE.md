# 🚀 TEKOSECURE - GUÍA DE INICIO RÁPIDO

**Versión:** 2.0 - Launcher Maestro  
**Fecha:** 24 Julio 2026  
**Sistema:** Windows PowerShell + Cloudflare Tunnel

---

## 📋 TABLA DE CONTENIDOS

1. [Inicio Rápido (30 segundos)](#inicio-rápido)
2. [Métodos de Ejecución](#métodos-de-ejecución)
3. [Solución de Problemas](#solución-de-problemas)
4. [Logs y Monitoreo](#logs-y-monitoreo)
5. [Detener el Sistema](#detener-el-sistema)

---

## 🎯 INICIO RÁPIDO

### Opción A: Acceso Directo en Desktop (RECOMENDADO)

**Primera vez SOLO:**
```bash
# 1. Abre CMD o PowerShell
# 2. Ejecuta esto:
cd C:\Users\TI\Desktop\Tekosecure
cscript scripts\setup\create-shortcut.vbs
```

**Aparecerá un diálogo confirmando que el acceso directo fue creado.**

**Luego, cada vez que quieras iniciar TEKOSECURE:**
- **Simplemente haz doble clic en `TEKOSECURE.lnk` en tu Desktop**
- El sistema se iniciará completamente en 10-15 segundos
- Se abrirá automáticamente tu navegador en https://tekosecurity.vercel.app
- Verás los logs en tiempo real en una ventana de PowerShell

---

### Opción B: Ejecución Manual Directa

**Si prefieres ejecutar manualmente sin crear acceso directo:**

```powershell
# Desde PowerShell, en el directorio de TEKOSECURE:
cd C:\Users\TI\Desktop\Tekosecure
.\scripts\startup\tekosecure-launcher.ps1
```

---

## 🔧 MÉTODOS DE EJECUCIÓN

### 1️⃣ **Modo Normal (Recomendado para Desarrollo)**
Ventana PowerShell visible con logs en tiempo real.

```bash
cscript C:\Users\TI\Desktop\Tekosecure\scripts\startup\tekosecure-launcher.vbs
```

**Ventajas:**
- ✓ Ver logs en tiempo real
- ✓ Fácil debug si hay errores
- ✓ Verifica startup correctamente

### 2️⃣ **Modo Silencioso (Producción)**
Ejecución en background sin ventanas visibles. Los logs se guardan en archivos.

```bash
cscript C:\Users\TI\Desktop\Tekosecure\scripts\startup\tekosecure-launcher-silent.vbs
```

**Ventajas:**
- ✓ Sin distracciones en pantalla
- ✓ Ideal para auto-arranque
- ✓ Logs en `C:\Users\TI\Desktop\Tekosecure\logs\launcher\`

### 3️⃣ **Ejecución Directa (PowerShell)**

**Con logs visibles:**
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\TI\Desktop\Tekosecure\scripts\startup\tekosecure-launcher.ps1"
```

**Silenciosa:**
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\TI\Desktop\Tekosecure\scripts\startup\tekosecure-launcher.ps1" -LogOnly
```

---

## 📊 QUÉ HACE EL LAUNCHER

El script maestro realiza esto automáticamente:

```
┌─────────────────────────────────────────────┐
│   TEKOSECURE LAUNCHER MAESTRO               │
├─────────────────────────────────────────────┤
│  1. Inicia Backend FastAPI (localhost:8001) │
│     └─ Espera y verifica conectividad       │
│                                              │
│  2. Inicia Cloudflare Tunnel                │
│     └─ Mapea localhost:8001 → HTTPS        │
│     └─ Espera y verifica conectividad       │
│                                              │
│  3. Abre navegador                          │
│     └─ https://tekosecurity.vercel.app     │
│                                              │
│  4. Mantiene ambos servicios activos        │
│     └─ Reinicia Tunnel si falla             │
│     └─ Registra todos los eventos          │
└─────────────────────────────────────────────┘
```

---

## ⏱️ TIMING ESPERADO

| Paso | Tiempo | Estado |
|------|--------|--------|
| Backend iniciando | 2-3s | 🟡 Iniciando |
| Backend verificado | 10-15s | 🟢 Listo |
| Tunnel iniciando | 3-5s | 🟡 Iniciando |
| Tunnel verificado | 10-15s | 🟢 Listo |
| Navegador abierto | Automático | 🟢 Accesible |
| **Total** | **~30 segundos** | **✅ Operativo** |

---

## 📍 PUNTOS DE ACCESO

Una vez iniciado, accede desde:

| Servicio | URL | Nota |
|----------|-----|------|
| **Frontend** | https://tekosecurity.vercel.app | Interfaz web |
| **Backend Local** | http://localhost:8001 | Solo desarrollo |
| **Tunnel Público** | https://api-tekosecure.nasser.com | Producción |
| **Health Check** | http://localhost:8001/api/health | Verificación |

---

## 🧪 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "Python no encontrado"
```bash
# Verificar que Python está instalado
python --version

# Si no está:
# Instala desde https://python.org (asegúrate de agregar a PATH)
```

### ❌ Error: "Wrangler no encontrado"
```bash
# Instalar wrangler globalmente
npm install -g @cloudflare/wrangler

# Verificar
wrangler --version
```

### ❌ Error: "Puerto 8001 en uso"
```bash
# Encuentra qué proceso usa el puerto
netstat -ano | findstr ":8001"

# Mata el proceso (reemplaza PID)
taskkill /PID <PID> /F
```

### ❌ El Tunnel no conecta
```bash
# Verifica que el archivo config existe
dir C:\Users\TI\Desktop\Tekosecure\tunnel\config.yml

# Verifica credenciales de Cloudflare
wrangler tunnel list

# Si es necesario, re-crea el tunnel
wrangler tunnel create tekosecure
```

### ⚠️ El navegador no abre automáticamente
- Abre manualmente: https://tekosecurity.vercel.app
- El backend está funcionando en background

---

## 📋 LOGS Y MONITOREO

### Ver logs en tiempo real
```bash
# Si ejecutas con ventana visible:
# Los logs aparecen en la ventana PowerShell

# Si ejecutas silencioso:
cd C:\Users\TI\Desktop\Tekosecure\logs\launcher
# Ver el archivo más reciente
type tekosecure-20260724-HHMMSS.log
```

### Archivos de logs

```
C:\Users\TI\Desktop\Tekosecure\logs\launcher\
├── tekosecure-20260724-090000.log     (Launcher maestro)
├── backend.log                         (FastAPI output)
├── backend-error.log                   (FastAPI errores)
├── tunnel.log                          (Cloudflare Tunnel)
└── tunnel-error.log                    (Tunnel errores)
```

### Monitorear procesos activos
```powershell
# Ver si Backend está corriendo
Get-Process python | findstr uvicorn

# Ver si Tunnel está corriendo
Get-Process | findstr wrangler

# Ver puertos en uso
netstat -ano | findstr "8001"
```

---

## 🛑 DETENER EL SISTEMA

### Opción 1: Cerrar la ventana PowerShell
- Simplemente cierra la ventana del launcher
- Se detendrán Backend y Tunnel automáticamente

### Opción 2: PowerShell (si ejecutaste silencioso)
```powershell
# Detener Backend
Stop-Process -Name python -Force

# Detener Tunnel
Stop-Process -Name wrangler -Force
```

### Opción 3: Task Manager
1. Abre Task Manager (Ctrl+Shift+Esc)
2. Busca "python.exe"
3. Haz clic derecho → End Task
4. Busca "wrangler"
5. Haz clic derecho → End Task

---

## ✅ CHECKLIST DE VERIFICACIÓN

Después de iniciar, verifica:

- [ ] Backend respondiendo en http://localhost:8001/api/health (HTTP 200)
- [ ] Navegador abierto en https://tekosecurity.vercel.app
- [ ] Dashboard visible con datos de NVRs y Mikrotik
- [ ] Puedes hacer login con credenciales de Supabase
- [ ] Logs muestran "TEKOSECURE OPERATIVO"

---

## 🔄 AUTO-ARRANQUE (Opcional)

Para iniciar TEKOSECURE automáticamente al encender:

1. **Presiona:** `Win + R`
2. **Escribe:** `shell:startup`
3. **Arrastra:** El acceso directo `TEKOSECURE.lnk` a esa carpeta
4. **Listo:** Se iniciará automáticamente al siguiente reinicio

---

## 📞 SOPORTE

Si tienes problemas:

1. **Verifica logs:** `C:\Users\TI\Desktop\Tekosecure\logs\launcher\`
2. **Intenta reiniciar:** Cierra y abre nuevamente
3. **Verifica conexión:** `ping api-tekosecure.nasser.com`
4. **Revisa firewall:** Puerto 8001 debe estar permitido localmente

---

## 🎯 FLUJO COMPLETO DE USO

```
Usuario hace clic en TEKOSECURE.lnk
    ↓
VBScript ejecuta PowerShell
    ↓
Launcher inicia Backend (FastAPI)
    ↓
Launcher verifica Backend (http://localhost:8001/api/health)
    ↓
Launcher inicia Tunnel (Cloudflare)
    ↓
Launcher verifica Tunnel (https://api-tekosecure.nasser.com/api/health)
    ↓
Launcher abre navegador (https://tekosecurity.vercel.app)
    ↓
📊 Dashboard en vivo con:
   • KPIs (Alertas activas, NVRs online, Ataques hoy)
   • Mapa de Mikrotik en tiempo real
   • Timeline de eventos de seguridad
   • Reportes con datos de Supabase
    ↓
Usuario puede:
   • Bloquear IPs maliciosas
   • Ver métricas de Mikrotik en vivo
   • Generar reportes ejecutivos
   • Monitorear 5 sucursales + 3 depósitos
```

---

## 🔐 SEGURIDAD

- Backend + Tunnel se inician SOLO si credenciales son válidas
- .env contiene secretos (nunca subir a git)
- CORS restringido a dominios autorizados
- JWT validado en cada request
- Audit log de todas las acciones

---

## 📊 ARQUITECTURA SIMPLIFICADA

```
┌─────────────────┐
│  Tu PC Windows  │
├─────────────────┤
│                 │
│  Python Backend │───→ localhost:8001
│  (FastAPI)      │
│                 │
│  Wrangler Tunnel├──────┐
│                 │      │
└─────────────────┘      │
                         │ HTTPS
                         │
                    ┌────▼─────────┐
                    │ Cloudflare   │
                    │ Edge Network │
                    └────┬─────────┘
                         │
                    ┌────▼──────────────┐
                    │ https://api-     │
                    │ tekosecure.      │
                    │ nasser.com       │
                    └────┬──────────────┘
                         │ HTTPS
                         │
        ┌────────────────┴──────────────┐
        │                               │
    ┌───▼────────┐            ┌────────▼──┐
    │  Vercel    │            │  Supabase │
    │  Frontend  │            │  Database │
    │  (React)   │            └───────────┘
    └────────────┘
```

---

**TEKOSECURE v2.0 - Iniciador Maestro**  
**Un clic y TODO funciona. Seguridad en tiempo real lista para usar.**

