# ============================================================================
# TEKOSECURE - Cloudflare Tunnel Startup
# ============================================================================

$TunnelDir = "C:\Users\TI\Desktop\Tekosecure"

Write-Host "==================== TEKOSECURE TUNNEL ===================="
Write-Host ""

Write-Host "Iniciando Cloudflare Tunnel..."
Write-Host ""

wrangler tunnel run --config $TunnelDir\tunnel\config.yml tekosecure

Write-Host ""
Write-Host "Tunnel detenido."
