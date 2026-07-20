# TEKOSECURE

**Sistema Integral de Monitoreo y Ciberseguridad de Red en Tiempo Real**

Solución empresarial de seguridad que monitorea infraestructura de redes, detecta ataques y genera alertas automáticas.

## 🎯 Características

- ✅ **Monitoreo Mikrotik en Tiempo Real**: Conexiones, ancho de banda, interfaces
- ✅ **Detección de Ataques**: Fuerza bruta, DDoS, escaneo de puertos, tráfico anómalo
- ✅ **Monitoreo Hikvision**: 9 NVRs distribuidos en sucursales
- ✅ **Credenciales Seguras**: Encriptación AES-256
- ✅ **Dashboard Visual**: Interfaz gráfica para alertas
- ✅ **Reportes Automáticos**: Generación mensual
- ✅ **Logs Auditables**: Registro completo de eventos

## 📊 Infraestructura Soportada

### Mikrotik
- Gateway: 192.168.13.100
- Monitoreo: SSH (puerto 22)
- Métricas: Conexiones, interfaces, rutas, firewall

### Hikvision NVRs
- **9 NVRs** distribuidos en 6 sucursales
- **154+ puertos** de video
- Modelos: DS-7216HUHI-K2, DS-7616NI-Q2, DS-7732NXI-K4, iDS-7616NXI-M2/X
- Ubicaciones: Matriz, Depósito KM7, Oasis, Zona Franca, Hernandarias, Ypané

## 🏗️ Estructura

```
TEKOSECURE/
├── config/
│   ├── network_config.json         # Configuración de red (plantilla)
│   ├── hikvision_devices.json      # Configuración de NVRs (plantilla)
│   ├── secure_config.py            # Gestor de credenciales
│   └── .env                        # Credenciales (NO VERSIONEAR)
├── scripts/
│   ├── monitor_mikrotik.py         # Monitoreo de router
│   ├── monitor_hikvision.py        # Monitoreo de cámaras
│   ├── detect_attacks.py           # Detector de anomalías
│   ├── alert_handler.py            # Gestor de alertas
│   └── test_connection.py          # Pruebas de conexión
├── dashboard/
│   └── TEKOSECURE_Dashboard.sln    # Proyecto Visual Studio (C#)
├── logs/
│   ├── network_events.log
│   ├── attacks_detected.log
│   └── hikvision_events.log
├── database/
│   └── tekosecure.db               # SQLite (NO VERSIONEAR)
└── docs/
    ├── INSTALLATION.md
    └── API.md
```

## 🚀 Instalación

### Requisitos
- Python 3.8+
- Windows/Linux
- Acceso SSH a Mikrotik
- Visual Studio 2022 (para dashboard)

### Setup

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/TEKOSECURE.git
cd TEKOSECURE

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar credenciales
cp config/.env.example config/.env
# Editar config/.env con tus credenciales

# 4. Probar conexión
python scripts/test_connection.py
```

## 📋 Configuración Requerida

### `.env` (NUNCA compartir)
```
MASTER_PASSWORD=tu_contraseña_maestra
MIKROTIK_PASSWORD=contraseña_encriptada
HIKVISION_PASS_1=contraseña_encriptada
...
```

### `network_config.json`
```json
{
  "mikrotik": {
    "ip": "192.168.13.100",
    "username": "admin",
    "port": 22
  },
  "alert_thresholds": {
    "failed_login_attempts": 5,
    "ddos_packet_rate": 10000
  }
}
```

### `hikvision_devices.json`
Configuración de 9 NVRs con IPs, usuarios y ubicaciones.

## 🔍 Detección de Amenazas

| Amenaza | Umbral | Acción |
|---------|--------|--------|
| Fuerza Bruta | 5 intentos en 5 min | Bloquear IP |
| DDoS | 10,000 paq/seg | Alerta CRITICAL |
| Escaneo Puertos | 10+ puertos | Alerta MEDIUM |
| Tráfico Anómalo | >85% BW | Alerta MEDIUM |
| NVR Offline | Cualquiera | Alerta HIGH |

## 💾 Base de Datos

SQLite con tabla de eventos:

```sql
CREATE TABLE attacks (
  id INTEGER PRIMARY KEY,
  timestamp DATETIME,
  attack_type TEXT,
  source_ip TEXT,
  severity TEXT,
  details TEXT
);
```

## 📊 Dashboard

### Tecnologías Disponibles
- **C# WinForms** (incluido)
- **Emergent App** (recomendado)
- **React/Vue** (custom)
- **IA Integrada** (análisis automático)

### Funcionalidades
- Alertas en tiempo real
- Histórico de eventos
- Bloqueo manual de IPs
- Exportación de reportes
- Gráficos de tendencias

## 🔐 Seguridad

- ✅ Encriptación AES-256 de credenciales
- ✅ `.gitignore` para datos sensibles
- ✅ Sin credenciales en código
- ✅ Logs auditables
- ✅ Control de acceso

## 📈 Reportes

Generación automática mensual:
- Ataques detectados
- IPs bloqueadas
- Estadísticas de red
- Estado de equipos

## 🤖 IA/ML (Próximo)

Integración con:
- LM Studio (local)
- Claude API
- Análisis predictivo
- Clasificación automática

## 🛠️ Desarrollo

```bash
# Ejecutar monitoreo
python scripts/monitor_mikrotik.py
python scripts/monitor_hikvision.py

# Probar ataques (simulación)
python scripts/detect_attacks.py --test

# Dashboard
cd dashboard
dotnet build TEKOSECURE_Dashboard.sln
```

## 📝 Logs

- `logs/network_events.log` - Eventos de red
- `logs/attacks_detected.log` - Amenazas
- `logs/hikvision_events.log` - Estados de NVR

## ⚖️ Licencia

Privado - Nasser Cubiertas

## 📧 Soporte

- Issues: [GitHub Issues]
- Email: admin@nasser.com

---

**TEKOSECURE** - Seguridad en Tiempo Real ✅
