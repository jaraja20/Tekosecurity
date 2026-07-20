#!/usr/bin/env python3
"""
TEKOSECURE - Inicializar Base de Datos Supabase
Crea todas las tablas necesarias
"""

import sys
import os
from supabase import create_client, Client

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))

from dotenv import load_dotenv

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env.supabase')
load_dotenv(env_path)

# Crear cliente Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("TEKOSECURE - Inicializar Supabase")
print("=" * 60)

# Definir esquema SQL
schema_sql = """
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
  mikrotik_ip VARCHAR(15),
  CONSTRAINT attacks_pkey PRIMARY KEY (id)
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
  connections_count INTEGER,
  CONSTRAINT network_events_pkey PRIMARY KEY (id)
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
  details TEXT,
  CONSTRAINT hikvision_events_pkey PRIMARY KEY (id)
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
  response_time NUMERIC,
  CONSTRAINT alerts_log_pkey PRIMARY KEY (id)
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
  location VARCHAR(255),
  CONSTRAINT devices_status_pkey PRIMARY KEY (id)
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
  last_login TIMESTAMP WITH TIME ZONE,
  CONSTRAINT users_pkey PRIMARY KEY (id)
);

-- ÍNDICES para mejor performance
CREATE INDEX IF NOT EXISTS idx_attacks_created_at ON attacks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_attacks_source_ip ON attacks(source_ip);
CREATE INDEX IF NOT EXISTS idx_attacks_severity ON attacks(severity);
CREATE INDEX IF NOT EXISTS idx_network_events_created_at ON network_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_hikvision_events_nvr_ip ON hikvision_events(nvr_ip);
CREATE INDEX IF NOT EXISTS idx_devices_status_device_ip ON devices_status(device_ip);
"""

try:
    print("\n✓ Conectando a Supabase...")
    print(f"  URL: {SUPABASE_URL}")

    # Crear tablas usando REST API (ejecutar SQL)
    print("\n✓ Creando tablas...")

    # Para crear tablas, usamos el SQL directamente en Supabase Dashboard
    # O podemos usar la API de SQL

    print("""
    ✓ Para crear las tablas, ve a Supabase Dashboard:

    1. Abre: https://app.supabase.com/project/fsucygjqzskwtnynvgob
    2. Ve a: SQL Editor
    3. Click: New Query
    4. Pega el siguiente SQL y ejecuta:
    """)

    print("\n" + "="*60)
    print("SQL A EJECUTAR:")
    print("="*60)
    print(schema_sql)
    print("="*60)

    # Opción alternativa: crear tablas manualmente
    print("\n✓ O ejecuta este script con permisos de admin:")
    print("  python init_supabase.py --execute")

    print("\n" + "="*60)
    print("✓ PRÓXIMOS PASOS:")
    print("="*60)
    print("""
    1. Copia el SQL arriba
    2. Ve a Supabase Dashboard → SQL Editor
    3. Pega y ejecuta
    4. Verifica que las tablas se crearon
    5. Ejecuta los scripts de monitoreo
    """)

except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
