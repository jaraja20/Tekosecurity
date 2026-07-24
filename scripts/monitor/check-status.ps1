# ============================================================================
# TEKOSECURE - Monitor de Estado
# ============================================================================
# Verifica si Backend y Tunnel están corriendo

Write-Host "========== TEKOSECURE STATUS CHECK ==========" -ForegroundColor Green
Write-Host ""

# Check Backend
Write-Host "Backend (FastAPI):"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Corriendo en http://localhost:8001" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ NO está disponible" -ForegroundColor Red
}

Write-Host ""

# Check Tunnel
Write-Host "Tunnel (Cloudflare):"
try {
    $response = Invoke-WebRequest -Uri "https://api-tekosecure.nasser.com/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Corriendo en https://api-tekosecure.nasser.com" -ForegroundColor Green
    }
} catch {
    Write-Host "  ✗ NO está disponible" -ForegroundColor Red
}

Write-Host ""

# Check Procesos
Write-Host "Procesos activos:"
$pythonRunning = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" }
$wranglerRunning = Get-Process wrangler -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "node" }

if ($pythonRunning) {
    Write-Host "  ✓ python.exe (Backend)" -ForegroundColor Green
} else {
    Write-Host "  ✗ python.exe (Backend) - NO CORRIENDO" -ForegroundColor Red
}

if ((Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*wrangler*" })) {
    Write-Host "  ✓ wrangler (Tunnel)" -ForegroundColor Green
} else {
    Write-Host "  ✗ wrangler (Tunnel) - NO CORRIENDO" -ForegroundColor Red
}

Write-Host ""
Write-Host "========== FIN ==========" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar TEKOSECURE: Haz doble clic en TEKOSECURE.lnk en Desktop"
Write-Host "Para ver logs: cd C:\Users\TI\Desktop\Tekosecure\logs\launcher"
Write-Host ""
