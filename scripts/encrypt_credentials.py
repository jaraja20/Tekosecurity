"""
Cifra las credenciales de Mikrotik usando AES-256
Guarda la clave en .env
"""

import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import hashlib

def generate_key(password: str) -> bytes:
    """Genera clave Fernet desde password"""
    # Hash del password para generar clave de 32 bytes
    hash_obj = hashlib.sha256(password.encode())
    key = base64.urlsafe_b64encode(hash_obj.digest())
    return key

def encrypt_password(password: str, key: bytes) -> str:
    """Cifra una contraseña"""
    cipher = Fernet(key)
    encrypted = cipher.encrypt(password.encode())
    return encrypted.decode()

def decrypt_password(encrypted: str, key: bytes) -> str:
    """Descifra una contraseña"""
    cipher = Fernet(key)
    decrypted = cipher.decrypt(encrypted.encode())
    return decrypted.decode()

# Leer config actual
config_path = Path(__file__).parent.parent / "config" / "mikrotik_config.json"
with open(config_path) as f:
    config = json.load(f)

# Generar clave (basada en una master key)
MASTER_PASSWORD = "TekosecureNasserTi@2024"  # ← CAMBIAR ESTO A ALGO SECRETO
key = generate_key(MASTER_PASSWORD)

print("🔐 Cifrando credenciales...")
print(f"Master Key para .env: {MASTER_PASSWORD}")

# Cifrar passwords
for mk in config["mikrotiks"]:
    original_password = mk["password"]
    encrypted_password = encrypt_password(original_password, key)
    mk["password"] = f"ENCRYPTED[{encrypted_password}]"
    print(f"✓ {mk['name']}: password cifrado")

# Guardar config cifrada
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"\n✓ Config guardada en {config_path}")

# Crear/actualizar .env
env_path = Path(__file__).parent.parent / ".env"
env_content = f"""# TEKOSECURE Credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Mikrotik Encryption Master Key
MIKROTIK_MASTER_KEY={MASTER_PASSWORD}
"""

# Leer .env existente si existe
if env_path.exists():
    with open(env_path) as f:
        existing = f.read()
    # Solo agregar si no existen
    if "MIKROTIK_MASTER_KEY" not in existing:
        with open(env_path, 'a') as f:
            f.write("\n# Mikrotik Encryption Master Key\n")
            f.write(f"MIKROTIK_MASTER_KEY={MASTER_PASSWORD}\n")
        print(f"✓ .env actualizado con credenciales de cifrado")
else:
    with open(env_path, 'w') as f:
        f.write(env_content)
    print(f"✓ .env creado con credenciales de cifrado")

print("\n⚠️  IMPORTANTE:")
print("1. Guarda la MASTER_KEY en un lugar seguro")
print("2. Cambia 'TekosecureNasserTi@2024' por una contraseña fuerte")
print("3. El .env debe estar en .gitignore (no subir a GitHub)")
print("\n✓ Credenciales cifradas exitosamente")
