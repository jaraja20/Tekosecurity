# TEKOSECURE - Brief para Emergent App

## 📋 OBJETIVO GENERAL

Crear un dashboard interactivo en tiempo real que monitoree:
- **Mikrotik**: Gateway de red (conexiones, interfaces, ancho de banda)
- **Hikvision**: 9 NVRs (estado, disponibilidad, eventos)
- **Ataques**: Detectar y bloquear automáticamente
- **Alertas**: Notificaciones en tiempo real

---

## 🗄️ BASE DE DATOS: SUPABASE PostgreSQL

### Credenciales de Conexión

```javascript
const { createClient } = require('@supabase/supabase-js')

const SUPABASE_URL = 'https://fsucygjqzskwtnynvgob.supabase.co'
const SUPABASE_ANON_KEY = 'sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
```

### Tablas Disponibles

#### 1. **attacks** (Ataques Detectados)

```sql
{
  id: BIGINT (PK),
  created_at: TIMESTAMP,
  attack_type: VARCHAR(50),  -- BRUTE_FORCE, DDoS, PORT_SCAN, ANOMALOUS_TRAFFIC
  source_ip: INET,
  destination_ip: INET,
  severity: VARCHAR(20),  -- LOW, MEDIUM, HIGH, CRITICAL
  details: TEXT,
  status: VARCHAR(20),  -- ACTIVE, CLOSED
  mikrotik_ip: VARCHAR(15)
}
```

**Ejemplo de datos:**
```json
{
  "id": 1,
  "created_at": "2026-07-20T14:30:00Z",
  "attack_type": "BRUTE_FORCE",
  "source_ip": "192.168.1.50",
  "severity": "HIGH",
  "details": "5 intentos fallidos en 5 minutos",
  "status": "ACTIVE"
}
```

#### 2. **hikvision_events** (Estado de NVRs)

```sql
{
  id: BIGINT (PK),
  created_at: TIMESTAMP,
  nvr_id: INTEGER,
  nvr_name: VARCHAR(255),
  nvr_ip: INET,
  event_type: VARCHAR(50),  -- STATUS_CHECK
  status: VARCHAR(20),  -- ONLINE, OFFLINE, ERROR
  model: VARCHAR(100),
  port_count: INTEGER,
  location: VARCHAR(255),
  details: TEXT
}
```

**Ejemplo:**
```json
{
  "id": 1,
  "nvr_name": "Matriz KM6 - Principal",
  "nvr_ip": "192.168.13.188",
  "status": "ONLINE",
  "model": "DS-7216HUHI-K2",
  "port_count": 16,
  "location": "Casa Matriz"
}
```

#### 3. **network_events** (Eventos de Red)

```sql
{
  id: BIGINT (PK),
  created_at: TIMESTAMP,
  event_type: VARCHAR(50),
  device_ip: INET,
  device_name: VARCHAR(255),
  description: TEXT,
  severity: VARCHAR(20),
  interface_name: VARCHAR(50),
  bandwidth_usage: NUMERIC,  -- % de uso
  connections_count: INTEGER
}
```

#### 4. **alerts_log** (Historial de Alertas)

```sql
{
  id: BIGINT (PK),
  created_at: TIMESTAMP,
  attack_id: BIGINT (FK attacks),
  alert_type: VARCHAR(50),
  alert_message: TEXT,
  sent_to: VARCHAR(255),
  status: VARCHAR(20),  -- SENT, ACKNOWLEDGED
  response_time: NUMERIC
}
```

#### 5. **devices_status** (Estado de Dispositivos)

```sql
{
  id: BIGINT (PK),
  created_at: TIMESTAMP,
  device_type: VARCHAR(50),  -- MIKROTIK, NVR, CAMERA
  device_name: VARCHAR(255),
  device_ip: INET,
  status: VARCHAR(20),
  last_seen: TIMESTAMP,
  uptime_seconds: BIGINT,
  location: VARCHAR(255)
}
```

#### 6. **users** (Usuarios del Dashboard)

```sql
{
  id: BIGINT (PK),
  created_at: TIMESTAMP,
  email: VARCHAR(255) UNIQUE,
  username: VARCHAR(100) UNIQUE,
  password_hash: VARCHAR(255),
  role: VARCHAR(50),  -- admin, viewer, operator
  is_active: BOOLEAN,
  last_login: TIMESTAMP
}
```

---

## 📡 API REST (AUTOMÁTICA)

Supabase genera automáticamente una API REST para cada tabla.

### Obtener Alertas Activas

```bash
GET https://fsucygjqzskwtnynvgob.supabase.co/rest/v1/attacks?status=eq.ACTIVE&order=created_at.desc

Headers:
  Authorization: Bearer sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh
  Content-Type: application/json
```

### Obtener Estado de NVRs

```bash
GET https://fsucygjqzskwtnynvgob.supabase.co/rest/v1/hikvision_events?select=*&order=created_at.desc&limit=100
```

### Actualizar Alerta

```bash
PATCH https://fsucygjqzskwtnynvgob.supabase.co/rest/v1/attacks?id=eq.1

Body:
{
  "status": "CLOSED"
}
```

---

## 🎯 FUNCIONALIDADES REQUERIDAS

### 1. **Panel Principal (Dashboard)**

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│  TEKOSECURE Dashboard        [Tiempo Real]  [Refresh]│
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────┬─────────────┬─────────────┐        │
│  │ Alertas     │ NVRs Online │ Ataques Hoy │        │
│  │ Activas: 3  │ 8/9         │ 15          │        │
│  └─────────────┴─────────────┴─────────────┘        │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ ALERTAS EN TIEMPO REAL                          │ │
│  ├─────────────────────────────────────────────────┤ │
│  │ 🚨 CRITICAL | BRUTE_FORCE | 192.168.1.50        │ │
│  │    5 intentos fallidos en 5 min                  │ │
│  │    [Bloquear IP] [Más info]                      │ │
│  │                                                  │ │
│  │ ⚠️  HIGH    | NVR_OFFLINE | 192.168.15.252       │ │
│  │    Zona Franca Global - Sin conexión             │ │
│  │                                                  │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
└─────────────────────────────────────────────────────┘
```

**Métricas:**
- Total alertas activas (contador en tiempo real)
- NVRs online vs total
- Ataques detectados hoy
- Ancho de banda actual
- Conexiones activas

### 2. **Vista de Alertas**

**Columnas:**
- Timestamp (hace X minutos)
- Severidad (badge: CRITICAL/HIGH/MEDIUM/LOW)
- Tipo (BRUTE_FORCE, DDoS, PORT_SCAN, NVR_OFFLINE, etc.)
- IP Origen / Dispositivo
- Detalles (truncado, expandible)
- Acciones:
  - [Bloquear IP]
  - [Ver detalles]
  - [Marcar como resuelta]
  - [Más información]

**Filtros:**
- Por severidad
- Por tipo de ataque
- Por fecha
- Estado (Activas/Todas)

**Ordenamiento:**
- Por timestamp (reciente primero)
- Por severidad

### 3. **Vista de NVRs Hikvision**

**Tarjeta por NVR:**
```
┌─────────────────────────────┐
│ 📹 Matriz KM6 - Principal   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ Status: 🟢 ONLINE           │
│ IP: 192.168.13.188          │
│ Modelo: DS-7216HUHI-K2      │
│ Puertos: 16/16              │
│ Ubicación: Casa Matriz      │
│ Última conexión: Hace 2 min │
│                             │
│ [Ver cámaras] [Eventos]     │
└─────────────────────────────┘
```

**Vista por sucursal:**
- Tarjetas por NVR
- Color verde (ONLINE) / Rojo (OFFLINE)
- Información de disponibilidad
- Eventos recientes

**Información por NVR:**
- Estado
- Modelo
- Cantidad de puertos
- Ubicación
- Disponibilidad (%)
- Últimos eventos

### 4. **Vista de Estadísticas**

**Gráficos:**
1. **Ataques por tipo** (gráfico de barras)
   - Datos de últimos 7 días
   - Actualizar en tiempo real

2. **Ataques por severidad** (gráfico circular)
   - Distribución CRITICAL/HIGH/MEDIUM/LOW

3. **Disponibilidad de NVRs** (gráfico de línea)
   - % uptime por NVR
   - Últimos 30 días

4. **Timeline de alertas** (gráfico de línea)
   - Cantidad de alertas por hora
   - Últimas 24 horas

### 5. **Sistema de Autenticación**

**Login:**
- Email + Contraseña
- Usar tabla `users` en Supabase
- Guardar token en localStorage

**Roles:**
- **admin**: Acceso completo (bloquear IPs, cerrar alertas, generar reportes)
- **operator**: Ver alertas, bloquear IPs
- **viewer**: Solo lectura

### 6. **Notificaciones en Tiempo Real**

**Supabase Realtime:**
```javascript
supabase
  .from('attacks')
  .on('INSERT', payload => {
    // Nueva alerta detectada
    console.log('Nueva alerta:', payload.new)
    // Mostrar notificación, reproducir sonido, etc.
  })
  .subscribe()

supabase
  .from('hikvision_events')
  .on('INSERT', payload => {
    // Nuevo evento NVR
    if (payload.new.status === 'OFFLINE') {
      // Mostrar alerta urgente
    }
  })
  .subscribe()
```

### 7. **Acciones del Usuario**

**Bloquear IP:**
```javascript
// 1. Usuario click en [Bloquear IP]
// 2. Confirmar en modal
// 3. Backend ejecuta: fail2ban-client set sshd banip <ip>
// 4. Marcar en UI como bloqueada
```

**Cerrar Alerta:**
```javascript
// PATCH /attacks/{id}
supabase
  .from('attacks')
  .update({ status: 'CLOSED' })
  .eq('id', alertId)
  .execute()
```

**Ver Detalles:**
- Expandir fila en tabla
- Mostrar modal con:
  - Descripción completa
  - Timeline de eventos relacionados
  - IPs involucradas
  - Acciones tomadas

### 8. **Reportes**

**Generar Reporte:**
```javascript
// Button en navbar
// GET /api/report?month=7&year=2026
// Descargar PDF con:
//  - Estadísticas mensuales
//  - Ataques por tipo/severidad
//  - Estado de NVRs
//  - IPs bloqueadas
//  - Recomendaciones
```

---

## 🔌 TECNOLOGÍAS SUGERIDAS

### Frontend
- **React** o **Vue.js** (Emergent App probablemente tenga opciones)
- **Supabase JS Client** para conexión a BD
- **Realtime subscription** para actualizaciones en vivo
- **Gráficos**: Recharts, Chart.js o similar
- **UI**: Tailwind CSS, Bootstrap, o Material-UI
- **Alertas/Notificaciones**: Sonido + visual

### Conectar a Supabase

```bash
npm install @supabase/supabase-js
```

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://fsucygjqzskwtnynvgob.supabase.co',
  'sb_publishable_WcxQECMlstlvfuzPV7ag3Q_ynzG0hVh'
)

// Obtener alertas
const { data, error } = await supabase
  .from('attacks')
  .select('*')
  .eq('status', 'ACTIVE')
  .order('created_at', { ascending: false })
```

---

## 📊 DATOS DE EJEMPLO

### 9 NVRs Distribuidos

```json
{
  "nvrs": [
    {
      "id": 1,
      "name": "Matriz KM6 - Principal",
      "ip": "192.168.13.188",
      "location": "Casa Matriz",
      "modelo": "DS-7216HUHI-K2",
      "puertos": 16
    },
    {
      "id": 2,
      "name": "Matriz KM6 - Depósito",
      "ip": "192.168.13.20",
      "location": "Casa Matriz - Deposito y comedor",
      "modelo": "DS-7616NI-Q2",
      "puertos": 16
    },
    {
      "id": 3,
      "name": "Depósito KM7",
      "ip": "192.168.2.10",
      "location": "Deposito km7",
      "modelo": "DS-7732NXI-K4(D)",
      "puertos": 32
    },
    {
      "id": 4,
      "name": "Oasis - Centro",
      "ip": "192.168.12.244",
      "location": "Oasis",
      "modelo": "DS-7632NI-K2",
      "puertos": 32
    },
    {
      "id": 5,
      "name": "Zona Franca Global - NVR1",
      "ip": "192.168.15.252",
      "location": "Zona Franca Global",
      "modelo": "iDS-7616NXI-M2/X",
      "puertos": 16
    },
    {
      "id": 6,
      "name": "Zona Franca Global - NVR2",
      "ip": "192.168.15.250",
      "location": "Zona Franca Global - 2",
      "modelo": "iDS-7616NXI-M2/X",
      "puertos": 16
    },
    {
      "id": 7,
      "name": "Hernandarias",
      "ip": "192.168.16.177",
      "location": "Hernandarias",
      "modelo": "iDS-7616NXI-M2/X",
      "puertos": 16
    },
    {
      "id": 8,
      "name": "Ypane - Principal",
      "ip": "192.168.3.253",
      "location": "Ypane",
      "modelo": "iDS-7616NXI-M2/X",
      "puertos": 16
    },
    {
      "id": 9,
      "name": "Ypane - Depósito",
      "ip": "192.168.3.215",
      "location": "Ypane - Deposito",
      "modelo": "iDS-7616NXI-M2/X",
      "puertos": 16
    }
  ]
}
```

---

## 🎨 DISEÑO REFERENCIAS

**Colores:**
- CRITICAL: #FF0000 (Rojo)
- HIGH: #FF9800 (Naranja)
- MEDIUM: #FFC107 (Amarillo)
- LOW: #4CAF50 (Verde)
- ONLINE: #4CAF50 (Verde)
- OFFLINE: #F44336 (Rojo)

**Tipografía:**
- Títulos: Arial Bold 24px
- Subtítulos: Arial 18px
- Body: Arial 14px
- Monospace: Courier New (para IPs, comandos)

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Autenticación con Supabase
- [ ] Dashboard principal con métricas
- [ ] Vista de alertas en tiempo real
- [ ] Vista de NVRs por sucursal
- [ ] Gráficos de estadísticas
- [ ] Sistema de notificaciones sonoras
- [ ] Acción: Bloquear IP
- [ ] Acción: Cerrar alerta
- [ ] Filtros y búsqueda
- [ ] Generación de reportes
- [ ] Responsive design (mobile/desktop)
- [ ] Pruebas de rendimiento con Realtime

---

## 📞 SOPORTE BACKEND

El backend ejecuta continuamente:
- **Mikrotik Monitor** (cada 10s)
- **Hikvision Monitor** (cada 30s)
- **Alert Manager** (cada 60s)
- **Detección de Ataques** (en tiempo real)

Todo se registra automáticamente en Supabase.

---

## 🚀 DEPLOY

La aplicación Emergent App se conectará directamente a Supabase sin necesidad de servidor backend adicional.

---

**TEKOSECURE v1.0 | Seguridad en Tiempo Real** 🔐
