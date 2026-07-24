' ============================================================================
' TEKOSECURE - Silent Launcher (VBScript)
' ============================================================================
' Ejecuta PowerShell en segundo plano sin ventana visible
' Pero abre ventana de PowerShell visible para ver logs en tiempo real

Option Explicit
Dim objShell, strScriptPath, strPowerShellCmd

' Crear objeto shell
Set objShell = CreateObject("WScript.Shell")

' Ruta del script PowerShell maestro
strScriptPath = "C:\Users\TI\Desktop\Tekosecure\scripts\startup\tekosecure-launcher-v3.ps1"

' Comando PowerShell con ejecución de scripts habilitada
' -NoExit mantiene la ventana abierta para ver logs
' -ExecutionPolicy Bypass permite ejecutar sin restricciones
strPowerShellCmd = "powershell.exe -NoExit -ExecutionPolicy Bypass -File """ & strScriptPath & """"

' Ejecutar con ventana visible (estilo Normal)
' Cambiar a 0 si deseas ejecución completamente silenciosa
objShell.Run strPowerShellCmd, 1, False

' Limpiar
Set objShell = Nothing
