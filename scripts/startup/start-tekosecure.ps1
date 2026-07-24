# ============================================================================
# TEKOSECURE - Startup Script (Backend + Tunnel)
# ============================================================================

$BackendDir = "C:\Users\TI\Desktop\Tekosecure"
$LogDir = "$BackendDir\logs\startup"

# Crear carpeta de logs
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$LogFile = "$LogDir\tekosecure-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Log {
    param([string]$Message)
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -Path $LogFile -Value "[$timestamp] $Message"
    Write-Host "$timestamp - $Message"
}

Log "==================== TEKOSECURE STARTUP ===================="

# 1. Iniciar Backend FastAPI
Log "Iniciando Backend FastAPI en puerto 8001..."
try {
    $BackendProcess = Start-Process -FilePath "python" `
        -ArgumentList "-m uvicorn backend.server:app --host 0.0.0.0 --port 8001" `
        -WorkingDirectory $BackendDir `
        -WindowStyle Normal `
        -PassThru
    Log "✓ Backend iniciado - PID: $($BackendProcess.Id)"
} catch {
    Log "✗ Error al iniciar Backend: $_"
    exit 1
}

Start-Sleep -Seconds 3

# 2. Iniciar Cloudflare Tunnel
Log "Iniciando Cloudflare Tunnel..."
try {
    $TunnelProcess = Start-Process -FilePath "wrangler" `
        -ArgumentList "tunnel run --config $BackendDir\tunnel\config.yml api-tekosecure" `
        -WorkingDirectory $BackendDir `
        -WindowStyle Normal `
        -PassThru
    Log "✓ Tunnel iniciado - PID: $($TunnelProcess.Id)"
} catch {
    Log "⚠ Cloudflare Tunnel no disponible (ignorando)"
}

Log "==================== READY ===================="
Log "✓ Backend: http://localhost:8001"
Log "✓ Frontend: https://tekosecurity-[your-app].vercel.app"
Log ""
Log "Para ver logs: Get-Content '$LogFile' -Tail 50"

# Monitoreo y auto-restart
while ($true) {
    if ($BackendProcess.HasExited) {
        Log "✗ Backend se cerró. Reiniciando..."
        $BackendProcess = Start-Process -FilePath "python" `
            -ArgumentList "-m uvicorn backend.server:app --host 0.0.0.0 --port 8001" `
            -WorkingDirectory $BackendDir `
            -WindowStyle Normal `
            -PassThru
        Log "✓ Backend reiniciado - PID: $($BackendProcess.Id)"
    }
    Start-Sleep -Seconds 10
}
