#!/usr/bin/env python3
"""
TEKOSECURE - Main Controller
Coordina todos los monitores y sistemas
"""

import sys
import os
import logging
import time
from datetime import datetime
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))

# Importar los monitores
from monitor_mikrotik import MikrotikMonitor
from monitor_hikvision import HikvisionMonitor
from alert_manager import AlertManager
from detect_attacks import AttackDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tekosecure.log'),
        logging.StreamHandler()
    ]
)

class TekosecureController:
    def __init__(self):
        logging.info("=" * 80)
        logging.info("TEKOSECURE - Iniciando Sistema de Ciberseguridad")
        logging.info("=" * 80)

        self.mikrotik_monitor = MikrotikMonitor()
        self.hikvision_monitor = HikvisionMonitor()
        self.alert_manager = AlertManager()
        self.attack_detector = AttackDetector()

        logging.info("✓ Todos los componentes inicializados")

    def monitor_mikrotik_thread(self, interval=10):
        """Thread para monitorear Mikrotik"""
        logging.info(f"[THREAD] Mikrotik monitor iniciado (intervalo: {interval}s)")

        while True:
            try:
                self.mikrotik_monitor.monitor_once()
                time.sleep(interval)
            except Exception as e:
                logging.error(f"[THREAD] Error Mikrotik: {e}")
                time.sleep(interval)

    def monitor_hikvision_thread(self, interval=30):
        """Thread para monitorear Hikvision"""
        logging.info(f"[THREAD] Hikvision monitor iniciado (intervalo: {interval}s)")

        while True:
            try:
                self.hikvision_monitor.monitor_all_nvrs()
                time.sleep(interval)
            except Exception as e:
                logging.error(f"[THREAD] Error Hikvision: {e}")
                time.sleep(interval)

    def alert_check_thread(self, interval=60):
        """Thread para verificar alertas"""
        logging.info(f"[THREAD] Alert manager iniciado (intervalo: {interval}s)")

        while True:
            try:
                self.alert_manager.run_checks()
                time.sleep(interval)
            except Exception as e:
                logging.error(f"[THREAD] Error en alertas: {e}")
                time.sleep(interval)

    def start_monitoring(self):
        """Inicia todos los monitores en threads paralelos"""
        logging.info("\n🚀 INICIANDO MONITOREO EN PARALELO\n")

        # Crear threads
        t1 = threading.Thread(target=self.monitor_mikrotik_thread, args=(10,), daemon=True)
        t2 = threading.Thread(target=self.monitor_hikvision_thread, args=(30,), daemon=True)
        t3 = threading.Thread(target=self.alert_check_thread, args=(60,), daemon=True)

        # Iniciar threads
        t1.start()
        t2.start()
        t3.start()

        logging.info("✓ Todos los threads están corriendo")
        logging.info("\n" + "=" * 80)
        logging.info("TEKOSECURE OPERATIVO")
        logging.info("=" * 80)
        logging.info("Presiona Ctrl+C para detener\n")

        # Mantener main thread vivo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("\n\n⛔ Deteniendo TEKOSECURE...")
            logging.info("Todos los threads se detuvieron")
            sys.exit(0)

if __name__ == "__main__":
    controller = TekosecureController()
    controller.start_monitoring()
