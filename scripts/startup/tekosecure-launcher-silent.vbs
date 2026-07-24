' ============================================================================
' TEKOSECURE - Silent Launcher (Completamente en Background)
' ============================================================================
' Ejecuta todo en segundo plano sin ventanas visibles
' Los logs se guardan en C:\Users\TI\Desktop\Tekosecure\logs\launcher\

Option Explicit
Dim objShell, strScriptPath, strPowerShellCmd

' Crear objeto shell
Set objShell = CreateObject("WScript.Shell")

' Ruta del script PowerShell maestro
strScriptPath = "C:\Users\TI\Desktop\Tekosecure\scripts\startup\tekosecure-launcher.ps1"

' Comando PowerShell con parámetro -LogOnly para ejecución silenciosa
' Hide (0) = completamente silencioso
strPowerShellCmd = "powershell.exe -ExecutionPolicy Bypass -File """ & strScriptPath & """ -LogOnly"

' Ejecutar completamente oculto
objShell.Run strPowerShellCmd, 0, False

' Limpiar
Set objShell = Nothing
