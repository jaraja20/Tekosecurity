# Debug - Ver qué está pasando
cd C:\Users\TI\Desktop\Tekosecure

Write-Host "Verificando Python..."
python --version

Write-Host ""
Write-Host "Intentando iniciar FastAPI..."
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8001

Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
