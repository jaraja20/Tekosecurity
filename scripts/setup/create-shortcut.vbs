' ============================================================================
' TEKOSECURE - Crear Acceso Directo en Desktop
' ============================================================================
' Ejecuta esto UNA VEZ para crear el acceso directo

Option Explicit
Dim objShell, objDesktop, objShortcut, strShortcutPath, strVbsPath

' Crear objeto shell
Set objShell = CreateObject("WScript.Shell")

' Rutas
strVbsPath = "C:\Users\TI\Desktop\Tekosecure\scripts\startup\tekosecure-launcher.vbs"
strShortcutPath = objShell.SpecialFolders("Desktop") & "\TEKOSECURE.lnk"

' Crear acceso directo
Set objShortcut = objShell.CreateShortcut(strShortcutPath)

' Configurar propiedades del acceso directo
objShortcut.TargetPath = "wscript.exe"
objShortcut.Arguments = """" & strVbsPath & """"
objShortcut.WorkingDirectory = "C:\Users\TI\Desktop\Tekosecure"
objShortcut.Description = "TEKOSECURE - Iniciador de Seguridad en Tiempo Real"
objShortcut.IconLocation = "C:\Windows\System32\secpol.msc,0"

' Guardar el acceso directo
objShortcut.Save

' Mostrar confirmación
MsgBox "✓ Acceso directo creado en Desktop:" & vbCrLf & _
        "TEKOSECURE.lnk" & vbCrLf & vbCrLf & _
        "Simplemente haz doble clic para iniciar el sistema completo.", _
        vbInformation, "TEKOSECURE Setup"

' Limpiar
Set objShortcut = Nothing
Set objShell = Nothing
