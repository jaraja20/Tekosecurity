"""
TEKOSECURE Security Module
- Rate limiting
- Input validation
- CORS restrictions
- Security headers
- Attack prevention
"""

import re
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Callable

# Rate limiter por IP
_rate_limits = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 60
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15

def rate_limit(max_requests: int = MAX_REQUESTS_PER_MINUTE, window_minutes: int = 1):
    """Rate limiting por IP"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtener IP del cliente
            request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)

            client_ip = request.client.host
            now = datetime.now()

            # Limpiar requests viejos
            _rate_limits[client_ip] = [
                t for t in _rate_limits[client_ip]
                if (now - t).total_seconds() < window_minutes * 60
            ]

            # Verificar límite
            if len(_rate_limits[client_ip]) >= max_requests:
                return {
                    "error": "Too many requests. Try again later.",
                    "status_code": 429
                }

            # Registrar request
            _rate_limits[client_ip].append(now)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 255

def validate_ip(ip: str) -> bool:
    """Validar formato de IP"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False

    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)

def validate_password(password: str) -> tuple[bool, str]:
    """Validar contraseña segura"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"

    return True, ""

def sanitize_input(data: str, max_length: int = 255) -> str:
    """Sanitizar entrada para prevenir inyecciones"""
    if not isinstance(data, str):
        return ""

    # Limitar longitud
    data = data[:max_length]

    # Remover caracteres peligrosos
    dangerous_chars = ['\x00', '\n', '\r', '\t']
    for char in dangerous_chars:
        data = data.replace(char, '')

    return data.strip()

def check_login_attempts(ip: str) -> tuple[bool, str]:
    """Verificar intentos de login fallidos"""
    key = f"login_attempt_{ip}"
    # En producción usar Redis
    now = datetime.now()

    if key not in _rate_limits:
        _rate_limits[key] = []

    # Limpiar intentos viejos
    _rate_limits[key] = [
        t for t in _rate_limits[key]
        if (now - t).total_seconds() < LOGIN_LOCKOUT_MINUTES * 60
    ]

    if len(_rate_limits[key]) >= MAX_LOGIN_ATTEMPTS:
        return False, f"Too many login attempts. Try again in {LOGIN_LOCKOUT_MINUTES} minutes."

    return True, ""

def record_login_attempt(ip: str):
    """Registrar intento de login fallido"""
    key = f"login_attempt_{ip}"
    if key not in _rate_limits:
        _rate_limits[key] = []
    _rate_limits[key].append(datetime.now())

# Security Headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=(),"
}

# CORS Configuration - RESTRINGIDO
ALLOWED_ORIGINS = [
    "https://tekosecurity.vercel.app",
    "https://api-tekosecure.localhost.run",
]

# En desarrollo
if True:  # Cambiar a False en producción
    ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://localhost:8001",
    ])
