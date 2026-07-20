#!/usr/bin/env python3
"""
TEKOSECURE - Report Generator
Genera reportes mensuales en PDF
"""

import sys
import os
from datetime import datetime, timedelta
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))

from supabase_client import supabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ReportGenerator:
    def __init__(self):
        self.supabase = supabase
        self.month = datetime.now().month
        self.year = datetime.now().year
        logging.info(f"Report Generator inicializado para {self.month}/{self.year}")

    def get_month_attacks(self):
        """Obtiene ataques del mes actual"""
        try:
            start_date = datetime(self.year, self.month, 1).isoformat()

            # Calcular fin del mes
            if self.month == 12:
                end_date = datetime(self.year + 1, 1, 1).isoformat()
            else:
                end_date = datetime(self.year, self.month + 1, 1).isoformat()

            attacks = self.supabase.client.table('attacks')\
                .select('*')\
                .gte('created_at', start_date)\
                .lt('created_at', end_date)\
                .execute()

            return attacks.data if attacks.data else []

        except Exception as e:
            logging.error(f"Error obteniendo ataques: {e}")
            return []

    def get_attack_statistics(self, attacks):
        """Calcula estadísticas de ataques"""
        stats = {
            'total': len(attacks),
            'by_type': {},
            'by_severity': {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0
            },
            'blocked_ips': set()
        }

        for attack in attacks:
            # Por tipo
            attack_type = attack.get('attack_type', 'UNKNOWN')
            stats['by_type'][attack_type] = stats['by_type'].get(attack_type, 0) + 1

            # Por severidad
            severity = attack.get('severity', 'LOW')
            if severity in stats['by_severity']:
                stats['by_severity'][severity] += 1

            # IPs bloqueadas
            if attack.get('source_ip'):
                stats['blocked_ips'].add(attack['source_ip'])

        stats['blocked_ips'] = list(stats['blocked_ips'])
        return stats

    def get_nvr_status_report(self):
        """Obtiene reporte de estado de NVRs"""
        try:
            start_date = datetime(self.year, self.month, 1).isoformat()

            if self.month == 12:
                end_date = datetime(self.year + 1, 1, 1).isoformat()
            else:
                end_date = datetime(self.year, self.month + 1, 1).isoformat()

            events = self.supabase.client.table('hikvision_events')\
                .select('*')\
                .gte('created_at', start_date)\
                .lt('created_at', end_date)\
                .execute()

            nvr_stats = {}
            for event in events.data:
                nvr = event['nvr_name']
                if nvr not in nvr_stats:
                    nvr_stats[nvr] = {
                        'online': 0,
                        'offline': 0,
                        'errors': 0,
                        'location': event.get('location', 'Unknown')
                    }

                status = event.get('status', 'UNKNOWN').lower()
                if status == 'online':
                    nvr_stats[nvr]['online'] += 1
                elif status == 'offline':
                    nvr_stats[nvr]['offline'] += 1
                else:
                    nvr_stats[nvr]['errors'] += 1

            return nvr_stats

        except Exception as e:
            logging.error(f"Error obteniendo reporte NVR: {e}")
            return {}

    def generate_text_report(self):
        """Genera reporte en texto"""
        attacks = self.get_month_attacks()
        stats = self.get_attack_statistics(attacks)
        nvr_stats = self.get_nvr_status_report()

        report = f"""
================================================================================
TEKOSECURE - REPORTE DE SEGURIDAD
Período: {self.month:02d}/{self.year}
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

RESUMEN EJECUTIVO
================================================================================
Total de Ataques Detectados: {stats['total']}
IPs Únicas Bloqueadas: {len(stats['blocked_ips'])}
NVRs Monitoreados: {len(nvr_stats)}

ATAQUES POR SEVERIDAD
================================================================================
CRÍTICO:   {stats['by_severity']['CRITICAL']} eventos
ALTO:      {stats['by_severity']['HIGH']} eventos
MEDIO:     {stats['by_severity']['MEDIUM']} eventos
BAJO:      {stats['by_severity']['LOW']} eventos

ATAQUES POR TIPO
================================================================================
"""

        for attack_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
            report += f"{attack_type:20} : {count:5} eventos\n"

        report += f"""
IPS BLOQUEADAS (Muestra)
================================================================================
"""
        for ip in stats['blocked_ips'][:10]:  # Solo primeros 10
            report += f"• {ip}\n"

        if len(stats['blocked_ips']) > 10:
            report += f"... y {len(stats['blocked_ips']) - 10} IPs más\n"

        report += f"""
ESTADO DE NVRS HIKVISION
================================================================================
"""

        for nvr, data in nvr_stats.items():
            total = data['online'] + data['offline'] + data['errors']
            uptime = (data['online'] / total * 100) if total > 0 else 0

            report += f"""
{nvr}
  Ubicación: {data['location']}
  Chequeos Online: {data['online']}
  Chequeos Offline: {data['offline']}
  Errores: {data['errors']}
  Disponibilidad: {uptime:.1f}%
"""

        report += f"""
RECOMENDACIONES
================================================================================
1. Revisar IPs bloqueadas y patrones de ataque
2. Verificar estado de NVRs con baja disponibilidad
3. Implementar rotación de credenciales mensualmente
4. Revisar logs de intentos de acceso fallidos
5. Actualizar reglas de firewall según tendencias

================================================================================
TEKOSECURE v1.0 | Seguridad en Tiempo Real
================================================================================
"""

        return report

    def save_report(self, content):
        """Guarda reporte en archivo"""
        try:
            filename = f"reports/TEKOSECURE_Report_{self.year}{self.month:02d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            # Crear carpeta si no existe
            os.makedirs('reports', exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            logging.info(f"✓ Reporte guardado: {filename}")
            return filename

        except Exception as e:
            logging.error(f"Error guardando reporte: {e}")
            return None

    def generate_monthly_report(self):
        """Genera reporte mensual completo"""
        logging.info("=" * 80)
        logging.info(f"GENERANDO REPORTE MENSUAL: {self.month:02d}/{self.year}")
        logging.info("=" * 80)

        # Generar contenido
        content = self.generate_text_report()

        # Guardar
        filename = self.save_report(content)

        # Mostrar en pantalla
        print(content)

        logging.info("=" * 80)
        logging.info("✓ REPORTE COMPLETADO")
        logging.info("=" * 80)

        return filename

if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate_monthly_report()
