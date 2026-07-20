#!/usr/bin/env python3
"""
TEKOSECURE - Alert Manager
Gestiona alertas automáticas y notificaciones
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))

from supabase_client import supabase
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/alerts.log'),
        logging.StreamHandler()
    ]
)

class AlertManager:
    def __init__(self):
        env_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env.supabase')
        load_dotenv(env_path)

        self.supabase = supabase
        self.alert_thresholds = {
            'brute_force': 5,  # 5 intentos
            'ddos': 10000,  # paquetes/seg
            'anomalous_traffic': 85,  # % de BW
        }

        logging.info("Alert Manager inicializado")

    def check_critical_alerts(self):
        """Verifica alertas críticas de hace poco"""
        try:
            alerts = self.supabase.client.table('attacks')\
                .select('*')\
                .eq('status', 'ACTIVE')\
                .gte('created_at', (datetime.now() - timedelta(hours=1)).isoformat())\
                .execute()

            critical = [a for a in alerts.data if a['severity'] in ['CRITICAL', 'HIGH']]

            return critical
        except Exception as e:
            logging.error(f"Error checking alerts: {e}")
            return []

    def create_alert(self, attack_data, recipients=None):
        """Crea una alerta y la registra"""
        try:
            alert_data = {
                'alert_type': attack_data['attack_type'],
                'alert_message': f"{attack_data['attack_type']} desde {attack_data.get('source_ip', 'unknown')}",
                'sent_to': recipients or 'admin@nasser.com',
                'status': 'SENT',
                'response_time': 0
            }

            # Registrar ataque primero
            attack_id = self.supabase.log_attack(attack_data)

            # Registrar alerta
            if attack_id:
                alert_data['attack_id'] = attack_id['data'][0]['id'] if attack_id['data'] else None

            self.supabase.log_alert(alert_data)

            logging.warning(f"⚠️ ALERTA CREADA: {attack_data['attack_type']} - Severidad: {attack_data['severity']}")

            return True

        except Exception as e:
            logging.error(f"Error creando alerta: {e}")
            return False

    def check_brute_force_attacks(self):
        """Verifica ataques de fuerza bruta recientes"""
        try:
            attacks = self.supabase.client.table('attacks')\
                .select('*')\
                .eq('attack_type', 'BRUTE_FORCE')\
                .eq('status', 'ACTIVE')\
                .gte('created_at', (datetime.now() - timedelta(minutes=5)).isoformat())\
                .execute()

            if len(attacks.data) >= self.alert_thresholds['brute_force']:
                logging.warning(f"🚨 Posible ataque de fuerza bruta detectado: {len(attacks.data)} intentos")
                return True

            return False

        except Exception as e:
            logging.error(f"Error checking brute force: {e}")
            return False

    def check_ddos_attacks(self):
        """Verifica ataques DDoS"""
        try:
            attacks = self.supabase.client.table('attacks')\
                .select('*')\
                .eq('attack_type', 'DDoS')\
                .eq('status', 'ACTIVE')\
                .gte('created_at', (datetime.now() - timedelta(minutes=1)).isoformat())\
                .execute()

            if len(attacks.data) > 0:
                logging.critical(f"🚨🚨🚨 ALERTA DDoS: {len(attacks.data)} eventos detectados")
                return True

            return False

        except Exception as e:
            logging.error(f"Error checking DDoS: {e}")
            return False

    def check_nvr_offline(self):
        """Verifica si algún NVR está offline"""
        try:
            offline_events = self.supabase.client.table('hikvision_events')\
                .select('*')\
                .eq('status', 'OFFLINE')\
                .gte('created_at', (datetime.now() - timedelta(minutes=5)).isoformat())\
                .execute()

            if len(offline_events.data) > 0:
                for event in offline_events.data:
                    logging.warning(f"⚠️ NVR OFFLINE: {event['nvr_name']} ({event['nvr_ip']})")

                # Crear alerta
                self.create_alert({
                    'attack_type': 'NVR_OFFLINE',
                    'source_ip': offline_events.data[0]['nvr_ip'],
                    'severity': 'HIGH',
                    'details': f"{len(offline_events.data)} NVRs offline"
                })

                return True

            return False

        except Exception as e:
            logging.error(f"Error checking NVR status: {e}")
            return False

    def close_resolved_alerts(self):
        """Cierra alertas resueltas"""
        try:
            # Obtener alertas viejas (más de 24 horas)
            old_alerts = self.supabase.client.table('attacks')\
                .select('id')\
                .eq('status', 'ACTIVE')\
                .lte('created_at', (datetime.now() - timedelta(hours=24)).isoformat())\
                .execute()

            for alert in old_alerts.data:
                self.supabase.close_alert(alert['id'])

            if len(old_alerts.data) > 0:
                logging.info(f"✓ {len(old_alerts.data)} alertas cerradas (edad > 24h)")

        except Exception as e:
            logging.error(f"Error closing alerts: {e}")

    def get_alert_summary(self):
        """Obtiene resumen de alertas"""
        try:
            active = self.supabase.client.table('attacks')\
                .select('count', count='exact')\
                .eq('status', 'ACTIVE')\
                .execute()

            critical = self.supabase.client.table('attacks')\
                .select('count', count='exact')\
                .eq('status', 'ACTIVE')\
                .in_('severity', ['CRITICAL', 'HIGH'])\
                .execute()

            today_attacks = self.supabase.client.table('attacks')\
                .select('count', count='exact')\
                .gte('created_at', datetime.now().replace(hour=0, minute=0, second=0).isoformat())\
                .execute()

            return {
                'active': active.count,
                'critical': critical.count,
                'today': today_attacks.count
            }

        except Exception as e:
            logging.error(f"Error getting summary: {e}")
            return {}

    def run_checks(self):
        """Ejecuta todos los chequeos"""
        logging.info("=" * 70)
        logging.info(f"VERIFICACIÓN DE ALERTAS: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("=" * 70)

        # Realizar chequeos
        self.check_brute_force_attacks()
        self.check_ddos_attacks()
        self.check_nvr_offline()
        self.close_resolved_alerts()

        # Resumen
        summary = self.get_alert_summary()
        logging.info(f"\n📊 RESUMEN: Activas={summary.get('active', 0)}, Críticas={summary.get('critical', 0)}, Hoy={summary.get('today', 0)}")
        logging.info("=" * 70)

if __name__ == "__main__":
    manager = AlertManager()
    manager.run_checks()
