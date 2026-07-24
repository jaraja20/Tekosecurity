$DesktopPath = "$env:USERPROFILE\Desktop"
$ShortcutPath = "$DesktopPath\TEKOSECURE.lnk"
$ScriptPath = "C:\Users\TI\Desktop\Tekosecure\scripts\startup\start-tekosecure-debug.ps1"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
$Shortcut.WorkingDirectory = "C:\Users\TI\Desktop\Tekosecure"
$Shortcut.IconLocation = "C:\Windows\System32\cmd.exe,0"
$Shortcut.Description = "Inicia TEKOSECURE Backend + Tunnel (con ventanas visibles)"
$Shortcut.Save()

Write-Host "OK - Acceso directo TEKOSECURE creado/actualizado"
