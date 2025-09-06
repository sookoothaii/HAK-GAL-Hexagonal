# HAK_GAL Frontend Backup Manager
# Automatisches Backup vor Änderungen mit Rollback-Funktion

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend_backups\backup_$timestamp"
$sourceDir = "D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend"
$rollbackLog = "D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend_backups\rollback.log"

function Create-Backup {
    Write-Host "🔒 Creating Frontend Backup..." -ForegroundColor Cyan
    
    # Create backup directory
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Copy all frontend files
    Write-Host "📁 Backing up src directory..."
    Copy-Item -Path "$sourceDir\src" -Destination "$backupDir\src" -Recurse -Force
    
    Write-Host "📄 Backing up configuration files..."
    Copy-Item -Path "$sourceDir\package.json" -Destination "$backupDir\" -Force
    Copy-Item -Path "$sourceDir\package-lock.json" -Destination "$backupDir\" -Force -ErrorAction SilentlyContinue
    Copy-Item -Path "$sourceDir\.env" -Destination "$backupDir\" -Force
    Copy-Item -Path "$sourceDir\vite.config.ts" -Destination "$backupDir\" -Force
    Copy-Item -Path "$sourceDir\tsconfig.json" -Destination "$backupDir\" -Force
    
    # Create backup metadata
    $metadata = @{
        timestamp = $timestamp
        date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        files = (Get-ChildItem -Path $sourceDir -Recurse -File).Count
        size = (Get-ChildItem -Path $sourceDir -Recurse | Measure-Object -Property Length -Sum).Sum
        node_version = node --version
        npm_version = npm --version
    }
    
    $metadata | ConvertTo-Json | Out-File "$backupDir\backup_metadata.json"
    
    # Log backup
    Add-Content -Path $rollbackLog -Value "[$timestamp] Backup created: $backupDir"
    
    Write-Host "✅ Backup completed: $backupDir" -ForegroundColor Green
    Write-Host "📊 Total files backed up: $($metadata.files)" -ForegroundColor Yellow
    
    return $backupDir
}

function List-Backups {
    Write-Host "`n📋 Available Backups:" -ForegroundColor Cyan
    $backups = Get-ChildItem -Path "D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend_backups" -Directory | Sort-Object Name -Descending
    
    $index = 1
    foreach ($backup in $backups) {
        $metadataPath = Join-Path $backup.FullName "backup_metadata.json"
        if (Test-Path $metadataPath) {
            $metadata = Get-Content $metadataPath | ConvertFrom-Json
            Write-Host "[$index] $($backup.Name) - Created: $($metadata.date) - Files: $($metadata.files)"
        } else {
            Write-Host "[$index] $($backup.Name)"
        }
        $index++
    }
    
    return $backups
}

function Rollback-Frontend {
    param(
        [int]$BackupIndex = 0
    )
    
    $backups = Get-ChildItem -Path "D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend_backups" -Directory | Sort-Object Name -Descending
    
    if ($BackupIndex -eq 0) {
        $backups = List-Backups
        $selection = Read-Host "`nSelect backup number to rollback to"
        $BackupIndex = [int]$selection
    }
    
    if ($BackupIndex -gt 0 -and $BackupIndex -le $backups.Count) {
        $selectedBackup = $backups[$BackupIndex - 1]
        
        Write-Host "`n⚠️  WARNING: This will rollback to backup: $($selectedBackup.Name)" -ForegroundColor Yellow
        Write-Host "Current frontend will be backed up first." -ForegroundColor Cyan
        $confirm = Read-Host "Continue? (yes/no)"
        
        if ($confirm -eq "yes") {
            # Create backup of current state
            Write-Host "`n📦 Creating backup of current state before rollback..."
            $currentBackup = Create-Backup
            
            # Perform rollback
            Write-Host "`n🔄 Rolling back to: $($selectedBackup.Name)..." -ForegroundColor Cyan
            
            # Remove current src
            Remove-Item -Path "$sourceDir\src" -Recurse -Force
            
            # Restore from backup
            Copy-Item -Path "$($selectedBackup.FullName)\src" -Destination "$sourceDir\src" -Recurse -Force
            Copy-Item -Path "$($selectedBackup.FullName)\*.json" -Destination "$sourceDir\" -Force
            Copy-Item -Path "$($selectedBackup.FullName)\*.ts" -Destination "$sourceDir\" -Force
            Copy-Item -Path "$($selectedBackup.FullName)\.env" -Destination "$sourceDir\" -Force -ErrorAction SilentlyContinue
            
            # Log rollback
            Add-Content -Path $rollbackLog -Value "[$timestamp] Rolled back from $currentBackup to $($selectedBackup.FullName)"
            
            Write-Host "✅ Rollback completed!" -ForegroundColor Green
            Write-Host "📌 Previous state backed up to: $currentBackup" -ForegroundColor Yellow
            Write-Host "`n🔧 Run 'npm install' if package.json changed" -ForegroundColor Cyan
        } else {
            Write-Host "❌ Rollback cancelled" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Invalid selection" -ForegroundColor Red
    }
}

# Main menu
Write-Host "`n🛡️  HAK_GAL Frontend Backup Manager" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Magenta

$action = $args[0]

switch ($action) {
    "backup" {
        Create-Backup
    }
    "list" {
        List-Backups
    }
    "rollback" {
        Rollback-Frontend
    }
    default {
        Write-Host "`nUsage:" -ForegroundColor Yellow
        Write-Host "  .\backup_manager.ps1 backup    - Create a new backup"
        Write-Host "  .\backup_manager.ps1 list      - List all backups"
        Write-Host "  .\backup_manager.ps1 rollback  - Rollback to a previous backup"
        Write-Host "`nExample:" -ForegroundColor Cyan
        Write-Host "  .\backup_manager.ps1 backup"
    }
}
