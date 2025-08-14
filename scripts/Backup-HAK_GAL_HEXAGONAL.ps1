<#
.SYNOPSIS
  GUI-Backup-System für HAK_GAL_HEXAGONAL (Port 5001) – Full/Incremental, Excludes, Manifest, Scheduling.

.DESCRIPTION
  - Erstellt sichere ZIP-Backups des gesamten Projekts.
  - Unterstützt Full- und Incremental-Backups (per SHA256-Manifest-Diff).
  - Konfigurierbare Excludes (node_modules, venv, __pycache__, .git, Logs, Zips, Caches, Backups).
  - Kompressionsstufen (Optimal/Fastest/NoCompression) via Compress-Archive.
  - GUI mit WinForms (Browse, Checkboxes, Progress, Log-Ausgabe).
  - Optional: Scheduled Task anlegen (CLI-Fallback verfügbar).

.NOTES
  - PowerShell 5.1+ empfohlen (Windows 10+). Keine Fremdabhängigkeiten (7z optional für Encryption – nicht standardmäßig aktiv).
  - Standard-Quellpfad wird automatisch aus dem Skriptpfad ermittelt.
  - Manifest wird pro Backup im Zielordner gespeichert.

.PARAMETER Destination
  (Optional) Backup-Zielpfad (überschreibt GUI-Eingabe; ermöglicht headless Nutzung).

.PARAMETER Mode
  (Optional) Full | Incremental (Default: Full)

.PARAMETER Compression
  (Optional) Optimal | Fastest | NoCompression (Default: Optimal)

.PARAMETER Silent
  (Optional) Unterdrückt GUI, führt sofort mit Parametern aus (z. B. für Scheduled Tasks).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\Backup-HAK_GAL_HEXAGONAL.ps1 -Destination "D:\Backups" -Mode Full -Compression Optimal -Silent
#>

param(
  [string]$Destination,
  [ValidateSet('Full','Incremental')][string]$Mode = 'Full',
  [ValidateSet('Optimal','Fastest','NoCompression')][string]$Compression = 'Optimal',
  [switch]$Silent,
  [switch]$SkipLocked = $true,
  [switch]$EnableSQLiteBackup = $true
)

Add-Type -AssemblyName System.Windows.Forms | Out-Null
Add-Type -AssemblyName System.Drawing | Out-Null

function Get-ProjectRoot {
  # Robust Ermittlung des Skriptverzeichnisses: bevorzugt $PSScriptRoot/$PSCommandPath, Fallback: aktuelles Verzeichnis
  try {
    $base = $PSScriptRoot
    if (-not $base -or $base -eq '') { $base = Split-Path -Parent $PSCommandPath -ErrorAction SilentlyContinue }
    if (-not $base -or $base -eq '') { $base = Split-Path -Parent $MyInvocation.MyCommand.Path -ErrorAction SilentlyContinue }
    if (-not $base -or $base -eq '') { $base = (Get-Location).Path }
  } catch {
    $base = (Get-Location).Path
  }

  $candidate = $null
  try { $candidate = Resolve-Path (Join-Path $base '..') -ErrorAction SilentlyContinue } catch {}
  if ($candidate) {
    $probe = Join-Path $candidate 'src_hexagonal'
    if (Test-Path $probe) { return (Resolve-Path $candidate).Path }
  }

  $candidate2 = $null
  try { $candidate2 = Resolve-Path (Join-Path $base '../..') -ErrorAction SilentlyContinue } catch {}
  if ($candidate2 -and (Test-Path (Join-Path $candidate2 'src_hexagonal'))) { return (Resolve-Path $candidate2).Path }

  return (Resolve-Path $base).Path
}

function New-BackupName { param([string]$mode) ("hak_gal_hexagonal_backup_{0}_{1}.zip" -f ((Get-Date).ToString('yyyyMMdd_HHmmss')),$mode) }

function Get-DefaultExcludes {
  @('\\.git($|\\)','\\node_modules($|\\)','\\\.venv($|\\)','\\venv($|\\)','\\__pycache__($|\\)','\\backups($|\\)','\\logs($|\\)',
    '\\.pytest_cache($|\\)','\\.mypy_cache($|\\)','\\.DS_Store$','\\.idea($|\\)','\\.vscode($|\\)','\\.coverage$','\\.cache($|\\)',
    '\\.egg-info($|\\)','\\.ipynb_checkpoints($|\\)','\\.dist($|\\)','\\.build($|\\)','\\.parcel-cache($|\\)','\\.turbo($|\\)',
    '\\.next($|\\)','\\.pnpm-store($|\\)','\\.gitlab-ci.yml$','\\.github($|\\)')
}

function Get-AllFiles { param([string]$root,[string[]]$ExcludePatterns)
  $files = Get-ChildItem -Path $root -Recurse -File -Force -ErrorAction SilentlyContinue
  if (-not $files) { return @() }
  if ($ExcludePatterns -and $ExcludePatterns.Count -gt 0) {
    $regex = "(" + (($ExcludePatterns | ForEach-Object {[Regex]::Escape($_)}) -join "|") + ")"
    return $files | Where-Object { $_.FullName -notmatch $regex }
  }
  return $files
}

function Get-ManifestFromFiles { param([System.IO.FileInfo[]]$Files,[string]$ProjectRoot)
  $manifest = @{}
  $script:LockedFiles = @()
  foreach ($f in $Files) {
    try {
      $rel = ($f.FullName.Substring($ProjectRoot.Length)).TrimStart('\\')
      $h = Get-FileHash -Path $f.FullName -Algorithm SHA256 -ErrorAction Stop
      $manifest[$rel] = [ordered]@{ sha256=$h.Hash; size=$f.Length; mtime=$f.LastWriteTimeUtc.ToString('o'); locked=$false }
    } catch {
      # Datei gesperrt oder nicht lesbar: markieren und trotzdem im Manifest führen
      try { $rel = ($f.FullName.Substring($ProjectRoot.Length)).TrimStart('\\') } catch {}
      $manifest[$rel] = [ordered]@{ sha256=$null; size=$f.Length; mtime=$f.LastWriteTimeUtc.ToString('o'); locked=$true }
      $script:LockedFiles += $f.FullName
    }
  }
  return $manifest
}

function Load-LastManifest { param([string]$dest)
  try {
    $latest = Get-ChildItem -Path $dest -Filter '*.json' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) { return (Get-Content -Path $latest.FullName -Raw | ConvertFrom-Json) }
  } catch {}
  return $null
}

function Save-Manifest { param([hashtable]$Manifest,[string]$Path) ($Manifest | ConvertTo-Json -Depth 6) | Out-File -FilePath $Path -Encoding UTF8 -Force }

function New-TempStagingFromDiff { param([hashtable]$Current,[object]$Last,[string]$Root,[string]$Staging)
  New-Item -Path $Staging -ItemType Directory -Force | Out-Null
  $copied = 0
  foreach ($rel in $Current.Keys) {
    $cur = $Current[$rel]
    $prev = $null
    if ($Last -and $Last.PSObject.Properties.Name -contains $rel) { $prev = $Last.$rel }
    $changed = $true
    if ($prev) { if (($prev.sha256 -eq $cur.sha256) -and ([int64]$prev.size -eq [int64]$cur.size)) { $changed = $false } }
    if ($changed) { $src = Join-Path $Root $rel; $dst = Join-Path $Staging $rel; New-Item -Path (Split-Path -Parent $dst) -ItemType Directory -Force | Out-Null; Copy-Item -Path $src -Destination $dst -Force; $copied++ }
  }
  return $copied
}

function Compress-PathSafe { param([string]$SourcePath,[string]$ZipPath,[string]$Compression='Optimal') if (Test-Path $ZipPath) { Remove-Item -Path $ZipPath -Force }; Compress-Archive -Path (Join-Path $SourcePath '*') -DestinationPath $ZipPath -CompressionLevel $Compression -Force }

function Write-Log { param([System.Windows.Forms.TextBox]$tb,[string]$msg) $line = "$(Get-Date -Format 'HH:mm:ss')  $msg"; if ($tb) { $tb.AppendText($line + [Environment]::NewLine) } else { Write-Host $line } }

# Versucht für SQLite-Dateien ein konsistentes Backup via Python/sqlite3 vorzunehmen
function Invoke-SqliteBackup {
  param([string]$Source,[string]$Dest)
  try {
    $py = "import sqlite3,os; src=r'''$Source'''; dst=r'''$Dest'''; os.makedirs(os.path.dirname(dst), exist_ok=True); con=sqlite3.connect(src); out=sqlite3.connect(dst); con.backup(out); out.close(); con.close()"
    & python -c $py 2>$null | Out-Null
    return $true
  } catch { return $false }
}

$ProjectRoot = Get-ProjectRoot
$DefaultDest = Join-Path $ProjectRoot 'backups'
if (-not (Test-Path $DefaultDest)) { New-Item -Path $DefaultDest -ItemType Directory | Out-Null }

if ($Silent -and $Destination) {
  $ex = Get-DefaultExcludes
  $files = Get-AllFiles -root $ProjectRoot -ExcludePatterns $ex
  $manifest = Get-ManifestFromFiles -Files $files -ProjectRoot $ProjectRoot
  $zipName = New-BackupName -mode $Mode.ToLower()
  if (-not (Test-Path $Destination)) { New-Item -Path $Destination -ItemType Directory | Out-Null }
  $zipPath = Join-Path $Destination $zipName
  if ($Mode -eq 'Full') {
    $staging = New-Item -Path (Join-Path ([System.IO.Path]::GetTempPath()) ("hexa_backup_" + [guid]::NewGuid().Guid)) -ItemType Directory
    try {
      foreach ($f in $files) {
        $rel = ($f.FullName.Substring($ProjectRoot.Length)).TrimStart('\\'); $dst = Join-Path $staging.FullName $rel; New-Item -Path (Split-Path -Parent $dst) -ItemType Directory -Force | Out-Null
        try {
          Copy-Item -Path $f.FullName -Destination $dst -Force -ErrorAction Stop
        } catch {
          $ext = [System.IO.Path]::GetExtension($f.FullName).ToLowerInvariant()
          if ($ext -eq '.db' -and $EnableSQLiteBackup) {
            if (-not (Invoke-SqliteBackup -Source $f.FullName -Dest $dst)) {
              if (-not $SkipLocked) { throw }
            }
          } elseif ($SkipLocked) {
            # überspringen
          } else { throw }
        }
      }
      Compress-PathSafe -SourcePath $staging.FullName -ZipPath $zipPath -Compression $Compression
    } finally { Remove-Item -Path $staging.FullName -Recurse -Force -ErrorAction SilentlyContinue }
  } else {
    $last = Load-LastManifest -dest $Destination
    $staging = New-Item -Path (Join-Path ([System.IO.Path]::GetTempPath()) ("hexa_backup_inc_" + [guid]::NewGuid().Guid)) -ItemType Directory
    try {
      $null = New-TempStagingFromDiff -Current $manifest -Last $last -Root $ProjectRoot -Staging $staging.FullName
      # Ergänzung: Falls gesperrte Dateien im Diff liegen, best-effort kopieren
      foreach ($rel in $manifest.Keys) {
        $entry = $manifest[$rel]
        if ($entry.locked -eq $true) {
          $src = Join-Path $ProjectRoot $rel; $dst = Join-Path $staging.FullName $rel; New-Item -Path (Split-Path -Parent $dst) -ItemType Directory -Force | Out-Null
          try { Copy-Item -Path $src -Destination $dst -Force -ErrorAction Stop }
          catch {
            if ([System.IO.Path]::GetExtension($src).ToLowerInvariant() -eq '.db' -and $EnableSQLiteBackup) {
              [void](Invoke-SqliteBackup -Source $src -Dest $dst)
            }
          }
        }
      }
      Compress-PathSafe -SourcePath $staging.FullName -ZipPath $zipPath -Compression $Compression
    }
    finally { Remove-Item -Path $staging.FullName -Recurse -Force -ErrorAction SilentlyContinue }
  }
  Save-Manifest -Manifest $manifest -Path (Join-Path $Destination ($zipName.Replace('.zip','.json')))
  Write-Host "Backup abgeschlossen: $zipPath"
  exit 0
}

$form = New-Object System.Windows.Forms.Form
$form.Text = 'HAK_GAL_HEXAGONAL Backup System (GPT-5)'
$form.Size = New-Object System.Drawing.Size(860, 640)
$form.StartPosition = 'CenterScreen'
$form.Font = (New-Object System.Drawing.Font('Segoe UI', 9))

$lblSource = New-Object System.Windows.Forms.Label; $lblSource.Text='Source (auto)'; $lblSource.Location='20,20'; $lblSource.AutoSize=$true; $form.Controls.Add($lblSource)
$tbSource = New-Object System.Windows.Forms.TextBox; $tbSource.Location='20,40'; $tbSource.Size='700,24'; $tbSource.ReadOnly=$true; $tbSource.Text=$ProjectRoot; $form.Controls.Add($tbSource)
$lblDest = New-Object System.Windows.Forms.Label; $lblDest.Text='Destination'; $lblDest.Location='20,80'; $lblDest.AutoSize=$true; $form.Controls.Add($lblDest)
$tbDest = New-Object System.Windows.Forms.TextBox; $tbDest.Location='20,100'; $tbDest.Size='620,24'; $tbDest.Text=$DefaultDest; $form.Controls.Add($tbDest)
$btnBrowse = New-Object System.Windows.Forms.Button; $btnBrowse.Text='Browse...'; $btnBrowse.Location='650,98'; $btnBrowse.Add_Click({ $fbd=New-Object System.Windows.Forms.FolderBrowserDialog; $fbd.SelectedPath=$tbDest.Text; if ($fbd.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { $tbDest.Text=$fbd.SelectedPath } }); $form.Controls.Add($btnBrowse)

$grpMode = New-Object System.Windows.Forms.GroupBox; $grpMode.Text='Mode'; $grpMode.Location='20,140'; $grpMode.Size='240,80'
$rbFull = New-Object System.Windows.Forms.RadioButton; $rbFull.Text='Full'; $rbFull.Location='10,30'; $rbFull.Checked=$true; $grpMode.Controls.Add($rbFull)
$rbInc = New-Object System.Windows.Forms.RadioButton; $rbInc.Text='Incremental'; $rbInc.Location='100,30'; $grpMode.Controls.Add($rbInc)
$form.Controls.Add($grpMode)

$grpComp = New-Object System.Windows.Forms.GroupBox; $grpComp.Text='Compression'; $grpComp.Location='280,140'; $grpComp.Size='240,80'
$cbComp = New-Object System.Windows.Forms.ComboBox; $cbComp.DropDownStyle='DropDownList'; [void]$cbComp.Items.Add('Optimal'); [void]$cbComp.Items.Add('Fastest'); [void]$cbComp.Items.Add('NoCompression'); $cbComp.SelectedIndex=0; $cbComp.Location='10,30'; $cbComp.Width=200; $grpComp.Controls.Add($cbComp); $form.Controls.Add($grpComp)

$grpEx = New-Object System.Windows.Forms.GroupBox; $grpEx.Text='Excludes (recommended)'; $grpEx.Location='540,140'; $grpEx.Size='300,200'
$chkNode=New-Object System.Windows.Forms.CheckBox; $chkNode.Text='frontend/node_modules'; $chkNode.Location='10,25'; $chkNode.Checked=$true; $grpEx.Controls.Add($chkNode)
$chkVenv=New-Object System.Windows.Forms.CheckBox; $chkVenv.Text='venv/.venv'; $chkVenv.Location='10,50'; $chkVenv.Checked=$true; $grpEx.Controls.Add($chkVenv)
$chkGit=New-Object System.Windows.Forms.CheckBox; $chkGit.Text='.git'; $chkGit.Location='10,75'; $chkGit.Checked=$true; $grpEx.Controls.Add($chkGit)
$chkCaches=New-Object System.Windows.Forms.CheckBox; $chkCaches.Text='Caches (__pycache__, .pytest_cache, .mypy_cache)'; $chkCaches.Location='10,100'; $chkCaches.Checked=$true; $grpEx.Controls.Add($chkCaches)
$chkLogs=New-Object System.Windows.Forms.CheckBox; $chkLogs.Text='logs'; $chkLogs.Location='10,125'; $chkLogs.Checked=$true; $grpEx.Controls.Add($chkLogs)
$chkZips=New-Object System.Windows.Forms.CheckBox; $chkZips.Text='bestehende *.zip/*.json Backups'; $chkZips.Location='10,150'; $chkZips.Checked=$true; $grpEx.Controls.Add($chkZips)
$form.Controls.Add($grpEx)

$btnDry = New-Object System.Windows.Forms.Button; $btnDry.Text='Dry-Run (zähle Dateien)'; $btnDry.Location='20,240'; $btnDry.Width=200; $form.Controls.Add($btnDry)
$btnStart = New-Object System.Windows.Forms.Button; $btnStart.Text='Backup starten'; $btnStart.Location='240,240'; $btnStart.Width=160; $form.Controls.Add($btnStart)
$btnOpen = New-Object System.Windows.Forms.Button; $btnOpen.Text='Zielordner öffnen'; $btnOpen.Location='420,240'; $btnOpen.Width=160; $btnOpen.Add_Click({ if (Test-Path $tbDest.Text) { Start-Process explorer.exe $tbDest.Text } }); $form.Controls.Add($btnOpen)
$btnTask = New-Object System.Windows.Forms.Button; $btnTask.Text='Scheduled Task erstellen'; $btnTask.Location='600,240'; $btnTask.Width=180; $form.Controls.Add($btnTask)

$prog = New-Object System.Windows.Forms.ProgressBar; $prog.Location='20,290'; $prog.Size='820,20'; $form.Controls.Add($prog)
$tbLog = New-Object System.Windows.Forms.TextBox; $tbLog.Location='20,320'; $tbLog.Size='820,260'; $tbLog.Multiline=$true; $tbLog.ScrollBars='Vertical'; $tbLog.ReadOnly=$true; $form.Controls.Add($tbLog)

$btnDry.Add_Click({ Write-Log $tbLog "Scanne Dateien..."; $ex=Get-DefaultExcludes; if ($chkNode.Checked){$ex+="\\node_modules($|\\)"}; if ($chkVenv.Checked){$ex+="\\(\.venv|venv)($|\\)"}; if ($chkGit.Checked){$ex+="\\\.git($|\\)"}; if ($chkCaches.Checked){$ex+="\\(__pycache__|\\.pytest_cache|\\.mypy_cache)($|\\)"}; if ($chkLogs.Checked){$ex+="\\logs($|\\)"}; if ($chkZips.Checked){$ex+="\\backups($|\\)|\\.zip$|\\.json$"}; $files=Get-AllFiles -root $ProjectRoot -ExcludePatterns $ex; Write-Log $tbLog ("Gefundene Dateien (nach Excludes): {0}" -f ($files.Count)) })

$btnStart.Add_Click({ try { $prog.Value=0; $dest=$tbDest.Text; if (-not (Test-Path $dest)) { New-Item -Path $dest -ItemType Directory | Out-Null }; $mode= if ($rbInc.Checked){'Incremental'} else {'Full'}; $comp=$cbComp.SelectedItem;
  Write-Log $tbLog "Baue Dateiliste..."; $ex=Get-DefaultExcludes; if ($chkNode.Checked){$ex+="\\node_modules($|\\)"}; if ($chkVenv.Checked){$ex+="\\(\.venv|venv)($|\\)"}; if ($chkGit.Checked){$ex+="\\\.git($|\\)"}; if ($chkCaches.Checked){$ex+="\\(__pycache__|\\.pytest_cache|\\.mypy_cache)($|\\)"}; if ($chkLogs.Checked){$ex+="\\logs($|\\)"}; if ($chkZips.Checked){$ex+="\\backups($|\\)|\\.zip$"};
  $files=Get-AllFiles -root $ProjectRoot -ExcludePatterns $ex; if (-not $files -or $files.Count -eq 0) { Write-Log $tbLog "Keine Dateien gefunden."; return };
  $prog.Value=10; Write-Log $tbLog ("Berechne Manifest für {0} Dateien..." -f $files.Count); $manifest=Get-ManifestFromFiles -Files $files -ProjectRoot $ProjectRoot; $prog.Value=30;
  $zipName=New-BackupName -mode $mode.ToLower(); $zipPath=Join-Path $dest $zipName;
  if ($mode -eq 'Full') { Write-Log $tbLog "Erstelle FULL-Backup (Staging)..."; $staging=New-Item -Path (Join-Path ([System.IO.Path]::GetTempPath()) ("hexa_backup_"+[guid]::NewGuid().Guid)) -ItemType Directory; try { $count=0; foreach ($f in $files){ $count++; if ($count % 500 -eq 0){ $prog.Value=[Math]::Min(80, 30 + [int]($count / $files.Count * 40)) }; $rel=($f.FullName.Substring($ProjectRoot.Length)).TrimStart('\\'); $dst=Join-Path $staging.FullName $rel; New-Item -Path (Split-Path -Parent $dst) -ItemType Directory -Force | Out-Null; Copy-Item -Path $f.FullName -Destination $dst -Force }; $prog.Value=85; Write-Log $tbLog "Komprimiere..."; Compress-PathSafe -SourcePath $staging.FullName -ZipPath $zipPath -Compression $comp } finally { Remove-Item -Path $staging.FullName -Recurse -Force -ErrorAction SilentlyContinue } }
  else { Write-Log $tbLog "Erstelle INCREMENTAL-Backup (Diff gegen letztes Manifest)..."; $last=Load-LastManifest -dest $dest; $staging=New-Item -Path (Join-Path ([System.IO.Path]::GetTempPath()) ("hexa_backup_inc_"+[guid]::NewGuid().Guid)) -ItemType Directory; try { $copied=New-TempStagingFromDiff -Current $manifest -Last $last -Root $ProjectRoot -Staging $staging.FullName; Write-Log $tbLog ("Geänderte/Neue Dateien: {0}" -f $copied); $prog.Value=75; Write-Log $tbLog "Komprimiere..."; Compress-PathSafe -SourcePath $staging.FullName -ZipPath $zipPath -Compression $comp } finally { Remove-Item -Path $staging.FullName -Recurse -Force -ErrorAction SilentlyContinue } };
  $prog.Value=90; $manifestPath=Join-Path $dest ($zipName.Replace('.zip','.json')); Save-Manifest -Manifest $manifest -Path $manifestPath; $prog.Value=100; Write-Log $tbLog "Backup abgeschlossen: $zipPath"; Write-Log $tbLog "Manifest gespeichert: $manifestPath"; [System.Windows.Forms.MessageBox]::Show("Backup erfolgreich erstellt:`n$zipPath","Backup",'OK','Information') | Out-Null }
catch { [System.Windows.Forms.MessageBox]::Show("Fehler: $($_.Exception.Message)","Backup",'OK','Error') | Out-Null; Write-Log $tbLog ("Fehler: $($_.Exception.Message)") } })

$btnTask.Add_Click({ try { $dest=$tbDest.Text; if (-not (Test-Path $dest)) { New-Item -Path $dest -ItemType Directory | Out-Null }; $ps=(Get-Process -Id $PID).Path; $scriptPath=$PSCommandPath; if (-not $scriptPath -or $scriptPath -eq '') { $scriptPath=$MyInvocation.MyCommand.Path }; if (-not $scriptPath -or $scriptPath -eq '') { $scriptPath=Join-Path $ProjectRoot 'scripts\Backup-HAK_GAL_HEXAGONAL.ps1' }; $taskName='Backup_HAK_GAL_HEXAGONAL'; $mode= if ($rbInc.Checked){'Incremental'} else {'Full'}; $comp=$cbComp.SelectedItem; $args="-ExecutionPolicy Bypass -File `"$scriptPath`" -Destination `"$dest`" -Mode $mode -Compression $comp -Silent"; $action=New-ScheduledTaskAction -Execute $ps -Argument $args; $trigger=New-ScheduledTaskTrigger -Daily -At 03:15; Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description 'Nightly backup of HAK_GAL_HEXAGONAL' -Force | Out-Null; [System.Windows.Forms.MessageBox]::Show("Scheduled Task erstellt: $taskName (täglich 03:15)","Scheduler",'OK','Information') | Out-Null; Write-Log $tbLog "Scheduled Task angelegt (03:15 täglich)." }
catch { [System.Windows.Forms.MessageBox]::Show("Fehler beim Anlegen des Tasks: $($_.Exception.Message)","Scheduler",'OK','Error') | Out-Null; Write-Log $tbLog ("Scheduler-Fehler: $($_.Exception.Message)") } })

[void]$form.ShowDialog()
