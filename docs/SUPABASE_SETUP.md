# TEKOSECURE - Configuración Supabase

## 🚀 Setup Rápido

### 1. Instalar librería Supabase

```bash
pip install supabase
```

### 2. Crear Tablas en Supabase

Ve a: **https://app.supabase.com/project/fsucygjqzskwtnynvgob/sql/new**

Copia y ejecuta este SQL:

```sql
-- TABLA: attacks
CREATE TABLE IF NOT EXISTS attacks (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  attack_type VARCHAR(50) NOT NULL,
  source_ip INET,
  destination_ip INET,
  severity VARCHAR(20),
  details TEXT,
  status VARCHAR(20) DEFAULT 'ACTIVE',
  mikrotik_ip VARCHAR(15)
);

-- TABLA: network_events
CREATE TABLE IF NOT EXISTS network_events (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  event_type VARCHAR(50) NOT NULL,
  device_ip INET,
  device_name VARCHAR(255),
  description TEXT,
  severity VARCHAR(20),
  interface_name VARCHAR(50),
  bandwidth_usage NUMERIC,
  connections_count INTEGER
);

-- TABLA: hikvision_events
CREATE TABLE IF NOT EXISTS hikvision_events (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  nvr_id INTEGER,
  nvr_name VARCHAR(255),
  nvr_ip INET,
  event_type VARCHAR(50),
  status VARCHAR(20),
  model VARCHAR(100),
  port_count INTEGER,
  location VARCHAR(255),
  details TEXT
);

-- TABLA: alerts_log
CREATE TABLE IF NOT EXISTS alerts_log (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  attack_id BIGINT REFERENCES attacks(id),
  alert_type VARCHAR(50),
  alert_message TEXT,
  sent_to VARCHAR(255),
  status VARCHAR(20),
  response_time NUMERIC
);

-- TABLA: devices_status
CREATE TABLE IF NOT EXISTS devices_status (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  device_type VARCHAR(50),
  device_name VARCHAR(255),
  device_ip INET,
  status VARCHAR(20),
  last_seen TIMESTAMP WITH TIME ZONE,
  uptime_seconds BIGINT,
  location VARCHAR(255)
);

-- TABLA: users
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  email VARCHAR(255) UNIQUE,
  username VARCHAR(100) UNIQUE,
  password_hash VARCHAR(255),
  role VARCHAR(50),
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP WITH TIME ZONE
);

-- ÍNDICES
CREATE INDEX idx_attacks_created_at ON attacks(created_at DESC);
CREATE INDEX idx_attacks_source_ip ON attacks(source_ip);
CREATE INDEX idx_attacks_severity ON attacks(severity);
CREATE INDEX idx_network_events_created_at ON network_events(created_at DESC);
CREATE INDEX idx_hikvision_events_nvr_ip ON hikvision_events(nvr_ip);
CREATE INDEX idx_devices_status_device_ip ON devices_status(device_ip);
```

### 3. Actualizar .env.supabase

Las claves ya están configuradas en:
```
C:\Users\TI\Desktop\Tekosecure\config\.env.supabase
```

**NUNCA** compartas este archivo en GitHub.

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Usar en scripts

```python
from config.supabase_client import supabase

# Registrar ataque
supabase.log_attack({
    'attack_type': 'BRUTE_FORCE',
    'source_ip': '192.168.1.50',
    'severity': 'HIGH',
    'details': '5 intentos fallidos en 5 minutos'
})

# Obtener alertas activas
alerts = supabase.get_active_alerts()
```

---

## 📊 Tablas Disponibles

### `attacks`
Ataques y amenazas detectadas

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | ID único |
| created_at | TIMESTAMP | Fecha de detección |
| attack_type | VARCHAR | BRUTE_FORCE, DDoS, PORT_SCAN, etc. |
| source_ip | INET | IP de origen del ataque |
| destination_ip | INET | IP de destino |
| severity | VARCHAR | LOW, MEDIUM, HIGH, CRITICAL |
| details | TEXT | Detalles del ataque |
| status | VARCHAR | ACTIVE, CLOSED |

### `network_events`
Eventos de red y topología

| Campo | Tipo | Descripción |
|-------|------|-------------|
| event_type | VARCHAR | Interface up/down, bandwidth change, etc. |
| device_ip | INET | IP del dispositivo |
| device_name | VARCHAR | Nombre del dispositivo |

### `hikvision_events`
Estado de NVRs y cámaras

| Campo | Tipo | Descripción |
|-------|------|-------------|
| nvr_name | VARCHAR | Nombre del NVR |
| nvr_ip | INET | IP del NVR |
| status | VARCHAR | ONLINE, OFFLINE |
| location | VARCHAR | Ubicación física |

### `alerts_log`
Historial de alertas enviadas

### `devices_status`
Estado actual de dispositivos

### `users`
Usuarios del dashboard

---

## 🔐 Seguridad

- ✅ `.env.supabase` está en `.gitignore`
- ✅ Usa `ANON_KEY` para lecturas normales
- ✅ Usa `SERVICE_KEY` solo en backend
- ✅ Configura RLS (Row Level Security) en Supabase si es necesario

---

## 🧪 Prueba Rápida

```bash
python config/supabase_client.py
```

Debe mostrar:
```
✓ Supabase cliente funciona
  URL: https://fsucygjqzskwtnynvgob.supabase.co

Alertas recientes: 0
```

---

## 📈 Monitor en Tiempo Real

Supabase proporciona Realtime API gratis. El dashboard puede suscribirse a cambios:

```javascript
// En Emergent App/Frontend
const { data } = supabase
  .from('attacks')
  .on('*', payload => {
    console.log('Nuevo ataque:', payload)
  })
  .subscribe()
```

---

## 💾 Backups

Supabase automáticamente:
- ✅ Realiza backups diarios (gratis)
- ✅ Retiene 7 días de backups
- ✅ Permite descargar manualmente

Ver en: Supabase Dashboard → Backups

---

## ❓ Problemas?

### "relation 'attacks' does not exist"
→ Ejecuta el SQL de creación de tablas

### "permission denied"
→ Usa SERVICE_KEY en .env.supabase

### "too many connections"
→ Usa connection pooling en Supabase Dashboard

---

**¡TEKOSECURE + Supabase = Seguridad en Tiempo Real!** 🚀
