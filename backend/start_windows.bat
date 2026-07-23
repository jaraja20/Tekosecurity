@echo off
REM =====================================================================
REM  TEKOSECURE Backend — Windows launcher
REM
REM  Usage: double-click start_windows.bat OR run from cmd.exe:
REM     cd C:\Users\TI\Desktop\Tekosecure\backend
REM     start_windows.bat
REM
REM  Requirements:
REM   1) Python 3.11+ installed and on PATH  (https://python.org)
REM   2) File backend\.env created (see .env.example)
REM   3) LAN reachability to the 4 Mikrotiks (192.168.13.100, .12.1, .15.1, .16.1)
REM =====================================================================

setlocal
cd /d %~dp0

echo.
echo [TEKOSECURE] Preparing backend...
echo.

REM Create venv if missing
if not exist ".venv\Scripts\python.exe" (
  echo [TEKOSECURE] Creating virtualenv...
  python -m venv .venv
)

call .venv\Scripts\activate.bat

echo [TEKOSECURE] Installing / updating dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt

if not exist ".env" (
  echo.
  echo [ERROR] backend\.env not found. Copy .env.example to .env and fill it in.
  pause
  exit /b 1
)

if not exist "logs" mkdir logs

echo.
echo [TEKOSECURE] Starting FastAPI on http://0.0.0.0:8000
echo [TEKOSECURE] Health: http://localhost:8000/api/health
echo [TEKOSECURE] Press Ctrl+C to stop.
echo.

python -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level info

endlocal
