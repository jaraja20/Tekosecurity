# ============================================================================
# TEKOSECURE - Startup Script (Backend SOLO)
# ============================================================================

$BackendDir = "C:\Users\TI\Desktop\Tekosecure"

Write-Host "==================== TEKOSECURE STARTUP ===================="
Write-Host "Backend Directory: $BackendDir"
Write-Host ""

# 1. Iniciar Backend FastAPI
Write-Host "1. Iniciando Backend FastAPI en puerto 8001..."
try {
    Start-Process -FilePath "python" `
        -ArgumentList "-m uvicorn backend.server:app --host 0.0.0.0 --port 8001" `
        -WorkingDirectory $BackendDir `
        -WindowStyle Normal

    Write-Host "✓ Backend iniciado"
} catch {
    Write-Host "✗ Error al iniciar Backend: $_"
    Write-Host ""
    Write-Host "Presiona cualquier tecla para continuar..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "==================== READY ===================="
Write-Host "✓ Backend: http://localhost:8001"
Write-Host "✓ Frontend: https://tekosecurity.vercel.app"
Write-Host "✓ Prueba: curl http://localhost:8001/api/health"
Write-Host ""
Write-Host "Esta ventana se puede cerrar. El backend seguirá corriendo."
Write-Host ""
