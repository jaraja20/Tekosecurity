# ============================================================================
# TEKOSECURE - Launcher Maestro (Backend + Tunnel + Browser)
# ============================================================================
# Este script hace TODO automaticamente:
# 1. Inicia Backend (FastAPI)
# 2. Inicia Tunnel (Cloudflare)
# 3. Abre navegador a Vercel
# 4. Muestra logs en tiempo real

param(
    [switch]$Silent = $false,
    [switch]$LogOnly = $false
)

# Configuracion
$BackendDir = "C:\Users\TI\Desktop\Tekosecure"
$LogDir = "$BackendDir\logs\launcher"
$TunnelConfig = "$BackendDir\tunnel\config.yml"
$FrontendURL = "https://tekosecurity.vercel.app"
$BackendURL = "http://localhost:8001"
$TunnelURL = "https://api-tekosecure.nasser.com"

# Crear carpeta de logs
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$LogFile = "$LogDir\tekosecure-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Log {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $output = "[$timestamp] [$Type] $Message"
    Add-Content -Path $LogFile -Value $output

    if (!$LogOnly) {
        switch ($Type) {
            "ERROR"   { Write-Host $output -ForegroundColor Red }
            "SUCCESS" { Write-Host $output -ForegroundColor Green }
            "WARNING" { Write-Host $output -ForegroundColor Yellow }
            default   { Write-Host $output }
        }
    }
}

Log "========== TEKOSECURE LAUNCHER INICIADO =========="
Log "Backend: $BackendURL"
Log "Tunnel: $TunnelURL"
Log "Frontend: $FrontendURL"
Log ""

# 1. INICIAR BACKEND
Log "1. Iniciando Backend FastAPI..." "INFO"
try {
    $BackendJob = Start-Process -FilePath "python" `
        -ArgumentList "-m uvicorn backend.server:app --host 0.0.0.0 --port 8001 --log-level info" `
        -WorkingDirectory $BackendDir `
        -WindowStyle Hidden `
        -PassThru `
        -RedirectStandardOutput "$LogDir\backend.log" `
        -RedirectStandardError "$LogDir\backend-error.log"

    Log "[OK] Backend iniciado (PID: $($BackendJob.Id))" "SUCCESS"
    Start-Sleep -Seconds 3
} catch {
    Log "[ERROR] Error al iniciar Backend: $_" "ERROR"
    exit 1
}

# 2. VERIFICAR BACKEND
Log "2. Verificando Backend..." "INFO"
$BackendReady = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$BackendURL/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Log "[OK] Backend respondiendo correctamente" "SUCCESS"
            $BackendReady = $true
            break
        }
    } catch {
        Log "  Intento $i/10: Esperando backend..." "INFO"
        Start-Sleep -Seconds 1
    }
}

if (!$BackendReady) {
    Log "[ERROR] Backend no responde despues de 10 intentos" "ERROR"
    Stop-Process -Id $BackendJob.Id -Force
    exit 1
}

# 3. INICIAR TUNNEL
Log "3. Iniciando Cloudflare Tunnel..." "INFO"
try {
    $TunnelJob = Start-Process -FilePath "wrangler" `
        -ArgumentList "tunnel run --config $TunnelConfig tekosecure" `
        -WorkingDirectory $BackendDir `
        -WindowStyle Hidden `
        -PassThru `
        -RedirectStandardOutput "$LogDir\tunnel.log" `
        -RedirectStandardError "$LogDir\tunnel-error.log"

    Log "[OK] Tunnel iniciado (PID: $($TunnelJob.Id))" "SUCCESS"
    Start-Sleep -Seconds 5
} catch {
    Log "[ERROR] Error al iniciar Tunnel: $_" "ERROR"
    Stop-Process -Id $BackendJob.Id -Force
    exit 1
}

# 4. VERIFICAR TUNNEL
Log "4. Verificando Tunnel..." "INFO"
$TunnelReady = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$TunnelURL/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Log "[OK] Tunnel respondiendo correctamente" "SUCCESS"
            $TunnelReady = $true
            break
        }
    } catch {
        Log "  Intento $i/10: Esperando tunnel..." "INFO"
        Start-Sleep -Seconds 1
    }
}

# 5. ABRIR NAVEGADOR
Log "5. Abriendo navegador..." "INFO"
try {
    Start-Process $FrontendURL
    Log "[OK] Navegador abierto en $FrontendURL" "SUCCESS"
} catch {
    Log "[WARNING] No se pudo abrir navegador: $_" "WARNING"
}

Log ""
Log "========== TEKOSECURE OPERATIVO ==========" "SUCCESS"
Log "Backend: $BackendURL"
Log "Tunnel: $TunnelURL"
Log "Frontend: $FrontendURL"
Log ""
Log "Logs guardados en: $LogDir"
Log "Para detener: Cierra las ventanas de PowerShell"
Log ""

# Mantener scripts corriendo
while ($true) {
    # Verificar si los procesos aun estan corriendo
    if ($null -eq (Get-Process -Id $BackendJob.Id -ErrorAction SilentlyContinue)) {
        Log "[ERROR] Backend se detuvo inesperadamente" "ERROR"
        break
    }
    if ($null -eq (Get-Process -Id $TunnelJob.Id -ErrorAction SilentlyContinue)) {
        Log "[WARNING] Tunnel se detuvo inesperadamente" "WARNING"
        # Intentar reiniciar Tunnel
        Log "Reiniciando Tunnel..." "INFO"
        $TunnelJob = Start-Process -FilePath "wrangler" `
            -ArgumentList "tunnel run --config $TunnelConfig tekosecure" `
            -WorkingDirectory $BackendDir `
            -WindowStyle Hidden `
            -PassThru `
            -RedirectStandardOutput "$LogDir\tunnel.log" `
            -RedirectStandardError "$LogDir\tunnel-error.log"
    }

    Start-Sleep -Seconds 10
}

# Limpiar al cerrar
Log "Deteniendo TEKOSECURE..." "INFO"
Stop-Process -Id $BackendJob.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $TunnelJob.Id -Force -ErrorAction SilentlyContinue
Log "Detenido correctamente" "SUCCESS"
