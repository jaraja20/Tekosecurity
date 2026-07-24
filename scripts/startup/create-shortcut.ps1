$DesktopPath = "$env:USERPROFILE\Desktop"
$ShortcutPath = "$DesktopPath\TEKOSECURE.lnk"
$ScriptPath = "C:\Users\TI\Desktop\Tekosecure\scripts\startup\start-tekosecure.ps1"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ScriptPath`""
$Shortcut.WorkingDirectory = "C:\Users\TI\Desktop\Tekosecure"
$Shortcut.IconLocation = "C:\Windows\System32\cmd.exe,0"
$Shortcut.Description = "Inicia TEKOSECURE"
$Shortcut.Save()

Write-Host "OK - Acceso directo creado en Desktop"
