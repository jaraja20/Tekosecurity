#!/usr/bin/env python3
"""
TEKOSECURE - Monitor Mikrotik
Monitorea en tiempo real conexiones, ancho de banda e interfaces del Mikrotik
"""

import paramiko
import json
import logging
import time
from datetime import datetime
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/network_events.log'),
        logging.StreamHandler()
    ]
)

class MikrotikMonitor:
    def __init__(self, config_file='config/network_config.json'):
        try:
            with open(config_file) as f:
                self.config = json.load(f)
            self.mikrotik = self.config['mikrotik']
            self.ssh = None
            logging.info("Configuración cargada exitosamente")
        except Exception as e:
            logging.error(f"Error cargando configuración: {e}")
            sys.exit(1)
    
    def connect(self):
        """Conecta al Mikrotik por SSH"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                self.mikrotik['ip'],
                port=self.mikrotik['port'],
                username=self.mikrotik['username'],
                password=self.mikrotik['password'],
                look_for_keys=False,
                allow_agent=False
            )
            logging.info(f"Conectado a Mikrotik {self.mikrotik['ip']}")
            return True
        except Exception as e:
            logging.error(f"Error conectando a Mikrotik: {e}")
            return False
    
    def execute_command(self, command):
        """Ejecuta comando en Mikrotik"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            return output, error
        except Exception as e:
            logging.error(f"Error ejecutando comando {command}: {e}")
            return None, str(e)
    
    def get_connections(self):
        """Obtiene conexiones activas"""
        output, error = self.execute_command('/ip firewall connection print')
        if output:
            lines = output.split('\n')
            count = len([l for l in lines if l.strip() and not l.startswith('Flags')])
            logging.info(f"Conexiones activas: {count}")
            return count
        return 0
    
    def get_interfaces(self):
        """Obtiene estado de interfaces"""
        output, error = self.execute_command('/interface print')
        if output:
            logging.info("Interfaces monitoreadas:")
            for line in output.split('\n')[:10]:
                if line.strip():
                    logging.info(f"  {line}")
            return output
        return None
    
    def get_ip_addresses(self):
        """Obtiene direcciones IP configuradas"""
        output, error = self.execute_command('/ip address print')
        if output:
            logging.info("Direcciones IP activas:")
            for line in output.split('\n')[:10]:
                if line.strip() and '192.168' in line:
                    logging.info(f"  {line}")
            return output
        return None
    
    def get_routes(self):
        """Obtiene tabla de ruteo"""
        output, error = self.execute_command('/ip route print')
        if output:
            lines = output.split('\n')
            count = len([l for l in lines if l.strip() and l[0].isdigit()])
            logging.info(f"Rutas activas: {count}")
            return count
        return 0
    
    def get_firewall_rules(self):
        """Obtiene reglas de firewall"""
        output, error = self.execute_command('/ip firewall filter print')
        if output:
            lines = output.split('\n')
            count = len([l for l in lines if l.strip() and l[0].isdigit()])
            logging.info(f"Reglas de firewall: {count}")
            return count
        return 0
    
    def monitor_once(self):
        """Realiza un monitoreo único"""
        if not self.ssh or not self.ssh.get_transport().is_active():
            if not self.connect():
                return False
        
        logging.info("=" * 50)
        logging.info(f"MONITOREO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("=" * 50)
        
        # Obtener datos
        connections = self.get_connections()
        self.get_interfaces()
        self.get_ip_addresses()
        routes = self.get_routes()
        rules = self.get_firewall_rules()
        
        logging.info(f"Resumen: {connections} conexiones, {routes} rutas, {rules} reglas")
        logging.info("=" * 50)
        
        return True
    
    def monitor_continuous(self, interval=10):
        """Monitoreo continuo"""
        if not self.connect():
            return
        
        logging.info(f"Iniciando monitoreo continuo (intervalo: {interval}s)")
        
        try:
            while True:
                self.monitor_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Monitoreo detenido por usuario")
        except Exception as e:
            logging.error(f"Error en monitoreo continuo: {e}")
        finally:
            self.disconnect()
    
    def disconnect(self):
        """Desconecta del Mikrotik"""
        if self.ssh:
            self.ssh.close()
            logging.info("Desconectado de Mikrotik")

if __name__ == "__main__":
    monitor = MikrotikMonitor()
    interval = monitor.config.get('alert_thresholds', {}).get('monitor_interval', 10)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        monitor.monitor_once()
    else:
        monitor.monitor_continuous(interval)
