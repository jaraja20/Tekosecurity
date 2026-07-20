#!/usr/bin/env python3
"""
TEKOSECURE - Detector de Ataques
Detecta: Fuerza bruta, DDoS, Escaneo de puertos, Tráfico anómalo
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/attacks_detected.log'),
        logging.StreamHandler()
    ]
)

class AttackDetector:
    def __init__(self, config_file='config/network_config.json'):
        try:
            with open(config_file) as f:
                self.config = json.load(f)
            self.thresholds = self.config['alert_thresholds']
            self.failed_attempts = defaultdict(list)
            self.db = self.init_database()
            logging.info("Detector de ataques inicializado")
        except Exception as e:
            logging.error(f"Error inicializando detector: {e}")
            sys.exit(1)
    
    def init_database(self):
        """Inicializa base de datos SQLite"""
        try:
            conn = sqlite3.connect('database/tekosecure.db')
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                attack_type TEXT NOT NULL,
                source_ip TEXT,
                destination_ip TEXT,
                severity TEXT,
                details TEXT,
                status TEXT DEFAULT 'ACTIVE'
            )''')
            conn.commit()
            logging.info("Base de datos inicializada")
            return conn
        except Exception as e:
            logging.error(f"Error inicializando BD: {e}")
            return None
    
    def detect_brute_force(self, ip, attempt_type='ssh'):
        """Detecta intentos de fuerza bruta"""
        now = datetime.now()
        window = now - timedelta(seconds=self.thresholds['brute_force_window'])
        
        self.failed_attempts[ip] = [
            attempt for attempt in self.failed_attempts[ip]
            if attempt > window
        ]
        
        self.failed_attempts[ip].append(now)
        
        attempts_count = len(self.failed_attempts[ip])
        threshold = self.thresholds['failed_login_attempts']
        
        if attempts_count >= threshold:
            self.log_attack('BRUTE_FORCE', ip, '0.0.0.0', 'HIGH',
                          f'{attempt_type}: {attempts_count} intentos en {self.thresholds["brute_force_window"]}s')
            return True
        
        return False
    
    def detect_ddos(self, packet_rate, source_ip='0.0.0.0'):
        """Detecta ataques DDoS"""
        threshold = self.thresholds['ddos_packet_rate']
        
        if packet_rate > threshold:
            self.log_attack('DDoS', source_ip, '0.0.0.0', 'CRITICAL',
                          f'Tasa de paquetes anómala: {packet_rate} paq/seg (umbral: {threshold})')
            return True
        
        return False
    
    def detect_port_scan(self, connections_data):
        """Detecta escaneo de puertos"""
        port_connections = defaultdict(set)
        
        for conn in connections_data:
            src_ip = conn.get('src_ip')
            dst_port = conn.get('dst_port')
            
            if src_ip and dst_port:
                port_connections[src_ip].add(dst_port)
        
        suspicious_ips = []
        for src_ip, ports in port_connections.items():
            if len(ports) > 10:
                self.log_attack('PORT_SCAN', src_ip, '0.0.0.0', 'MEDIUM',
                              f'Escaneo de puertos: {len(ports)} puertos diferentes')
                suspicious_ips.append(src_ip)
        
        return len(suspicious_ips) > 0
    
    def detect_anomalous_traffic(self, bandwidth_usage):
        """Detecta tráfico anómalo"""
        threshold = self.thresholds['unusual_traffic_threshold']
        
        if bandwidth_usage > threshold:
            self.log_attack('ANOMALOUS_TRAFFIC', '0.0.0.0', '0.0.0.0', 'MEDIUM',
                          f'Uso de ancho de banda: {bandwidth_usage}% (umbral: {threshold}%)')
            return True
        
        return False
    
    def detect_connection_flood(self, connection_count):
        """Detecta flood de conexiones"""
        threshold = 1000  # Conexiones simultáneas
        
        if connection_count > threshold:
            self.log_attack('CONNECTION_FLOOD', '0.0.0.0', '0.0.0.0', 'HIGH',
                          f'Número anómalo de conexiones: {connection_count} (umbral: {threshold})')
            return True
        
        return False
    
    def detect_unauthorized_access(self, source_ip, target_port):
        """Detecta intentos de acceso no autorizado"""
        restricted_ports = [22, 23, 3389, 5900]  # SSH, Telnet, RDP, VNC
        
        if target_port in restricted_ports:
            self.log_attack('UNAUTHORIZED_ACCESS_ATTEMPT', source_ip, '0.0.0.0', 'HIGH',
                          f'Intento de acceso a puerto restringido {target_port}')
            return True
        
        return False
    
    def log_attack(self, attack_type, src_ip, dst_ip, severity, details):
        """Registra ataque en BD y log"""
        timestamp = datetime.now().isoformat()
        message = f'[{severity}] {attack_type} | Origen: {src_ip} | {details}'
        
        logging.warning(message)
        
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('''INSERT INTO attacks 
                                 (timestamp, attack_type, source_ip, destination_ip, severity, details)
                                 VALUES (?, ?, ?, ?, ?, ?)''',
                              (timestamp, attack_type, src_ip, dst_ip, severity, details))
                self.db.commit()
            except Exception as e:
                logging.error(f"Error guardando ataque en BD: {e}")
    
    def get_active_alerts(self):
        """Obtiene alertas activas"""
        if not self.db:
            return []
        
        try:
            cursor = self.db.cursor()
            cursor.execute('SELECT * FROM attacks WHERE status = "ACTIVE" ORDER BY timestamp DESC LIMIT 20')
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error obteniendo alertas: {e}")
            return []
    
    def test_detection(self):
        """Prueba funcionalidad de detección"""
        logging.info("Iniciando pruebas de detección...")
        
        # Test 1: Fuerza bruta
        logging.info("\nTest 1: Detectando fuerza bruta...")
        for i in range(6):
            self.detect_brute_force('192.168.13.50', 'ssh')
        
        # Test 2: DDoS
        logging.info("\nTest 2: Detectando DDoS...")
        self.detect_ddos(15000)
        
        # Test 3: Tráfico anómalo
        logging.info("\nTest 3: Detectando tráfico anómalo...")
        self.detect_anomalous_traffic(90)
        
        # Test 4: Conexiones
        logging.info("\nTest 4: Detectando flood de conexiones...")
        self.detect_connection_flood(1500)
        
        logging.info("\nPruebas completadas. Revisa logs/attacks_detected.log")

if __name__ == "__main__":
    detector = AttackDetector()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        detector.test_detection()
    else:
        logging.info("Detector de ataques activo (en espera de datos)")
        logging.info("Ejecuta con --test para pruebas")
