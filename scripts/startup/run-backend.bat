@echo off
cd /d "C:\Users\TI\Desktop\Tekosecure"
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8001 --log-level info
