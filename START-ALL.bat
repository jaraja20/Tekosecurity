@echo off
REM ============================================================================
REM TEKOSECURE - INICIO COMPLETO
REM ============================================================================

cd /d "C:\Users\TI\Desktop\Tekosecure"

REM Matar procesos anteriores
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak

REM Abrir 2 ventanas - Backend y Tunnel
start "TEKOSECURE - Backend" cmd /k "python -m uvicorn backend.server:app --host 0.0.0.0 --port 8001 --log-level info"
timeout /t 3 /nobreak

start "TEKOSECURE - Tunnel" cmd /k "wrangler tunnel run --config tunnel\config.yml tekosecure"
timeout /t 3 /nobreak

REM Abrir navegador
start "" https://tekosecurity.vercel.app

echo.
echo ============================================================
echo TEKOSECURE INICIADO
echo ============================================================
echo.
echo Backend: http://localhost:8001
echo Frontend: https://tekosecurity.vercel.app
echo Tunnel: https://api-tekosecure.nasser.com
echo.
echo Cierra estas ventanas para detener el sistema
echo.
pause
