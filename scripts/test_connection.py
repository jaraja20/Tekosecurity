#!/usr/bin/env python3
"""
TEKOSECURE - Prueba de Conexión a Mikrotik
"""

import sys
import os

# Agregar ruta de config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))

from secure_config import SecureConfigManager
import paramiko
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

print("=" * 60)
print("TEKOSECURE - PRUEBA DE CONEXIÓN A MIKROTIK")
print("=" * 60)

# Cargar configuración segura
print("\n1. Cargando configuración segura...")
try:
    manager = SecureConfigManager()
    creds = manager.get_mikrotik_credentials()
    
    if not creds:
        print("✗ Error: No se pudo desencriptar credenciales")
        sys.exit(1)
    
    print(f"✓ Configuración cargada")
    print(f"   IP: {creds['ip']}")
    print(f"   Usuario: {creds['username']}")
    print(f"   Puerto: {creds['port']}")
except Exception as e:
    print(f"✗ Error cargando configuración: {e}")
    sys.exit(1)

# Conectar a Mikrotik
print("\n2. Conectando a Mikrotik...")
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ssh.connect(
        creds['ip'],
        port=creds['port'],
        username=creds['username'],
        password=creds['password'],
        look_for_keys=False,
        allow_agent=False,
        timeout=10
    )
    print(f"✓ Conectado a {creds['ip']}")
except Exception as e:
    print(f"✗ Error de conexión: {e}")
    sys.exit(1)

# Ejecutar comandos de prueba
print("\n3. Obteniendo información del Mikrotik...")

comandos = [
    ('/system identity print', 'Identidad'),
    ('/interface print numbers=0..3', 'Interfaces'),
    ('/ip address print', 'Direcciones IP'),
    ('/ip firewall connection print numbers=0..4', 'Conexiones Activas'),
]

try:
    for comando, descripcion in comandos:
        print(f"\n   [{descripcion}]:")
        stdin, stdout, stderr = ssh.exec_command(comando)
        output = stdout.read().decode('utf-8', errors='ignore')
        
        lines = output.split('\n')[:6]
        for line in lines:
            if line.strip():
                print(f"   {line[:70]}")
        
        if len(output.split('\n')) > 6:
            print("   ...")
    
    print("\n" + "=" * 60)
    print("✓ PRUEBA EXITOSA - Conexión a Mikrotik funcionando")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error ejecutando comandos: {e}")
finally:
    ssh.close()

