#!/usr/bin/env python3
"""
TEKOSECURE - Supabase Client
Cliente para conectar y escribir datos en Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '.env.supabase')
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_ANON_KEY')

        if not self.url or not self.key:
            logger.error("Credenciales de Supabase no configuradas")
            raise ValueError("SUPABASE_URL y SUPABASE_ANON_KEY requeridas en .env.supabase")

        self.client: Client = create_client(self.url, self.key)
        logger.info("✓ Cliente Supabase inicializado")

    def log_attack(self, attack_data: dict):
        """Registra un ataque en la tabla attacks"""
        try:
            response = self.client.table('attacks').insert(attack_data).execute()
            logger.info(f"✓ Ataque registrado: {attack_data['attack_type']}")
            return response
        except Exception as e:
            logger.error(f"✗ Error registrando ataque: {e}")
            return None

    def log_network_event(self, event_data: dict):
        """Registra un evento de red"""
        try:
            response = self.client.table('network_events').insert(event_data).execute()
            logger.info(f"✓ Evento registrado: {event_data['event_type']}")
            return response
        except Exception as e:
            logger.error(f"✗ Error registrando evento: {e}")
            return None

    def log_hikvision_event(self, event_data: dict):
        """Registra un evento de Hikvision"""
        try:
            response = self.client.table('hikvision_events').insert(event_data).execute()
            logger.info(f"✓ Evento Hikvision registrado: {event_data['nvr_name']}")
            return response
        except Exception as e:
            logger.error(f"✗ Error registrando evento Hikvision: {e}")
            return None

    def log_alert(self, alert_data: dict):
        """Registra una alerta"""
        try:
            response = self.client.table('alerts_log').insert(alert_data).execute()
            logger.info(f"✓ Alerta registrada: {alert_data['alert_type']}")
            return response
        except Exception as e:
            logger.error(f"✗ Error registrando alerta: {e}")
            return None

    def update_device_status(self, device_data: dict):
        """Actualiza estado de un dispositivo"""
        try:
            response = self.client.table('devices_status').insert(device_data).execute()
            logger.info(f"✓ Estado actualizado: {device_data['device_name']}")
            return response
        except Exception as e:
            logger.error(f"✗ Error actualizando estado: {e}")
            return None

    def get_recent_attacks(self, limit=100):
        """Obtiene ataques recientes"""
        try:
            response = self.client.table('attacks')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"✗ Error obteniendo ataques: {e}")
            return []

    def get_active_alerts(self):
        """Obtiene alertas activas"""
        try:
            response = self.client.table('attacks')\
                .select('*')\
                .eq('status', 'ACTIVE')\
                .order('created_at', desc=True)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"✗ Error obteniendo alertas: {e}")
            return []

    def get_device_status(self, device_ip):
        """Obtiene estado de un dispositivo"""
        try:
            response = self.client.table('devices_status')\
                .select('*')\
                .eq('device_ip', device_ip)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"✗ Error obteniendo estado: {e}")
            return None

    def close_alert(self, alert_id):
        """Cierra una alerta"""
        try:
            response = self.client.table('attacks')\
                .update({'status': 'CLOSED'})\
                .eq('id', alert_id)\
                .execute()
            logger.info(f"✓ Alerta cerrada: {alert_id}")
            return response
        except Exception as e:
            logger.error(f"✗ Error cerrando alerta: {e}")
            return None

# Instancia global
try:
    supabase = SupabaseClient()
except Exception as e:
    logger.error(f"No se pudo inicializar Supabase: {e}")
    supabase = None

if __name__ == "__main__":
    # Test
    if supabase:
        print("✓ Supabase cliente funciona")
        print(f"  URL: {supabase.url}")

        # Obtener alertas recientes
        alerts = supabase.get_recent_attacks(limit=5)
        print(f"\nAlertas recientes: {len(alerts)}")
    else:
        print("✗ Error inicializando Supabase")
