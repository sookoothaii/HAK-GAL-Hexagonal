# Erstellt Desktop-Verknüpfungen für HAK_GAL
# Als Administrator ausführen für beste Ergebnisse

$WshShell = New-Object -comObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')

# Verknüpfung für START
$Shortcut = $WshShell.CreateShortcut("$Desktop\HAK_GAL Start.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"D:\MCP Mods\HAK_GAL_HEXAGONAL\START_ALL_SERVICES.ps1`""
$Shortcut.WorkingDirectory = "D:\MCP Mods\HAK_GAL_HEXAGONAL"
$Shortcut.IconLocation = "powershell.exe, 0"
$Shortcut.Description = "Startet alle HAK_GAL Services"
$Shortcut.Save()

Write-Host "✅ Desktop-Verknüpfung 'HAK_GAL Start' erstellt" -ForegroundColor Green

# Verknüpfung für STOP
$Shortcut = $WshShell.CreateShortcut("$Desktop\HAK_GAL Stop.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"D:\MCP Mods\HAK_GAL_HEXAGONAL\STOP_ALL_SERVICES.ps1`""
$Shortcut.WorkingDirectory = "D:\MCP Mods\HAK_GAL_HEXAGONAL"
$Shortcut.IconLocation = "powershell.exe, 1"
$Shortcut.Description = "Beendet alle HAK_GAL Services"
$Shortcut.Save()

Write-Host "✅ Desktop-Verknüpfung 'HAK_GAL Stop' erstellt" -ForegroundColor Green

# Alternative: Batch-Verknüpfung
$Shortcut = $WshShell.CreateShortcut("$Desktop\HAK_GAL Batch Start.lnk")
$Shortcut.TargetPath = "D:\MCP Mods\HAK_GAL_HEXAGONAL\START_HAK_GAL.bat"
$Shortcut.WorkingDirectory = "D:\MCP Mods\HAK_GAL_HEXAGONAL"
$Shortcut.IconLocation = "cmd.exe, 0"
$Shortcut.Description = "Startet alle HAK_GAL Services (Batch)"
$Shortcut.Save()

Write-Host "✅ Desktop-Verknüpfung 'HAK_GAL Batch Start' erstellt" -ForegroundColor Green

Write-Host ""
Write-Host "Alle Verknüpfungen wurden auf dem Desktop erstellt!" -ForegroundColor Cyan
Write-Host "Sie können jetzt HAK_GAL mit einem Doppelklick starten." -ForegroundColor Cyan
