@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM TEKOSECURE - Setup Inicial
REM ============================================================================
REM Este archivo crea todo lo necesario para usar TEKOSECURE

title TEKOSECURE - Setup

cls
echo.
echo ============================================================================
echo TEKOSECURE - Configuracion Inicial
echo ============================================================================
echo.
echo Este script va a:
echo  1. Crear acceso directo en Desktop
echo  2. Verificar dependencias (Python, wrangler)
echo  3. Listo para usar!
echo.

REM Verificar Python
echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python no esta instalado
    echo Descargalo desde https://python.org
    echo.
    pause
    exit /b 1
) else (
    echo  OK: Python instalado
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
    echo     Version: !PYTHON_VER!
)

REM Verificar FastAPI y dependencias
echo.
echo [1/3] Verificando modulos Python...
python -c "import fastapi, uvicorn, supabase, paramiko, cryptography" >nul 2>&1
if errorlevel 1 (
    echo  ADVERTENCIA: Faltan modulos Python
    echo  Ejecuta: pip install fastapi uvicorn supabase paramiko cryptography --break-system-packages
) else (
    echo  OK: Todos los modulos presentes
)

REM Verificar wrangler
echo.
echo [2/3] Verificando Cloudflare wrangler...
wrangler --version >nul 2>&1
if errorlevel 1 (
    echo  ADVERTENCIA: wrangler no esta instalado
    echo  Ejecuta: npm install -g @cloudflare/wrangler
) else (
    echo  OK: wrangler instalado
    for /f "tokens=*" %%i in ('wrangler --version 2^>^&1') do set WRANGLER_VER=%%i
    echo     Version: !WRANGLER_VER!
)

REM Crear acceso directo
echo.
echo [3/3] Creando acceso directo en Desktop...
cscript "C:\Users\TI\Desktop\Tekosecure\scripts\setup\create-shortcut.vbs"

echo.
echo ============================================================================
echo SETUP COMPLETADO
echo ============================================================================
echo.
echo SIGUIENTE PASO: Haz doble clic en TEKOSECURE.lnk en tu Desktop
echo.
pause
