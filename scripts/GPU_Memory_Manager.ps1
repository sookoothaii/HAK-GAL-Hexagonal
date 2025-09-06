# ============================================
# OLLAMA GPU MEMORY MANAGER
# Advanced VRAM management for Ollama models
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "OLLAMA GPU MEMORY MANAGER" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Function to get GPU memory usage
function Get-GPUMemory {
    $gpu_info = nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits
    if ($gpu_info) {
        $parts = $gpu_info -split ','
        $used = [int]$parts[0]
        $total = [int]$parts[1]
        $percent = [math]::Round(($used / $total) * 100, 1)
        
        Write-Host "GPU Memory: $used MB / $total MB ($percent%)" -ForegroundColor $(if ($percent -gt 80) {"Red"} elseif ($percent -gt 50) {"Yellow"} else {"Green"})
        return @{Used=$used; Total=$total; Percent=$percent}
    }
}

# Show current status
Write-Host "CURRENT GPU STATUS:" -ForegroundColor Yellow
Write-Host "-------------------" -ForegroundColor Gray
$before = Get-GPUMemory

# Check what's using GPU
Write-Host "`nPROCESSES USING GPU:" -ForegroundColor Yellow
Write-Host "--------------------" -ForegroundColor Gray
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader | ForEach-Object {
    if ($_) {
        Write-Host "  $_" -ForegroundColor White
    }
}

# Check Ollama status
Write-Host "`nOLLAMA STATUS:" -ForegroundColor Yellow
Write-Host "--------------" -ForegroundColor Gray
$ollama_running = Get-Process -Name "ollama*" -ErrorAction SilentlyContinue
if ($ollama_running) {
    Write-Host "  ✓ Ollama is running" -ForegroundColor Green
    
    # Try to get loaded models
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 2
        if ($response.models) {
            Write-Host "  Loaded models:" -ForegroundColor Cyan
            $response.models | ForEach-Object {
                $size_gb = [math]::Round($_.size / 1GB, 2)
                Write-Host "    - $($_.name) ($size_gb GB)" -ForegroundColor White
            }
        }
    } catch {
        Write-Host "  Could not query Ollama API" -ForegroundColor Gray
    }
} else {
    Write-Host "  ✗ Ollama not running" -ForegroundColor Red
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "CLEANUP OPTIONS:" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "1. Unload current model (keep Ollama running)" -ForegroundColor White
Write-Host "2. Stop Ollama completely" -ForegroundColor White
Write-Host "3. Force kill all GPU processes" -ForegroundColor White
Write-Host "4. Smart cleanup (unload large, load small)" -ForegroundColor White
Write-Host "5. Show GPU status only" -ForegroundColor White
Write-Host "0. Exit" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Select option [0-5]"

switch ($choice) {
    "1" {
        Write-Host "`nUnloading current model..." -ForegroundColor Yellow
        # Send keep_alive=0 to unload
        $body = @{
            model = "qwen2.5:32b-instruct-q3_K_M"
            keep_alive = 0
        } | ConvertTo-Json
        
        try {
            Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
            Write-Host "✓ Model unloaded" -ForegroundColor Green
        } catch {
            Write-Host "Could not unload via API, trying alternative..." -ForegroundColor Yellow
            # Load tiny model to push out big one
            Start-Process ollama -ArgumentList "run", "tinyllama", "exit" -Wait
        }
    }
    
    "2" {
        Write-Host "`nStopping Ollama..." -ForegroundColor Yellow
        Start-Process ollama -ArgumentList "stop" -Wait -NoNewWindow
        Stop-Process -Name "ollama*" -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Ollama stopped" -ForegroundColor Green
    }
    
    "3" {
        Write-Host "`nForce killing GPU processes..." -ForegroundColor Red
        Stop-Process -Name "ollama*" -Force -ErrorAction SilentlyContinue
        Stop-Process -Name "llama*" -Force -ErrorAction SilentlyContinue
        Stop-Process -Name "python*" -Force -ErrorAction SilentlyContinue
        
        # Try GPU reset
        Write-Host "Attempting GPU reset..." -ForegroundColor Yellow
        $reset = Start-Process nvidia-smi -ArgumentList "--gpu-reset" -Wait -PassThru -NoNewWindow
        if ($reset.ExitCode -eq 0) {
            Write-Host "✓ GPU reset successful" -ForegroundColor Green
        } else {
            Write-Host "⚠ GPU reset failed (processes still using GPU)" -ForegroundColor Yellow
        }
    }
    
    "4" {
        Write-Host "`nSmart cleanup..." -ForegroundColor Cyan
        Write-Host "1. Stopping current model..." -ForegroundColor Gray
        
        # First try to unload
        $body = @{model = ""; keep_alive = 0} | ConvertTo-Json
        try {
            Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
        } catch {}
        
        Start-Sleep -Seconds 2
        
        Write-Host "2. Loading tiny model to clear VRAM..." -ForegroundColor Gray
        Start-Process ollama -ArgumentList "run", "tinyllama", "exit" -Wait
        
        Write-Host "3. Unloading tiny model..." -ForegroundColor Gray
        Start-Process ollama -ArgumentList "stop" -Wait -NoNewWindow
        
        Write-Host "✓ Smart cleanup complete" -ForegroundColor Green
    }
    
    "5" {
        # Just show status, already displayed above
    }
    
    "0" {
        exit
    }
}

# Show final status
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "FINAL GPU STATUS:" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
$after = Get-GPUMemory

if ($before -and $after) {
    $freed = $before.Used - $after.Used
    if ($freed -gt 0) {
        Write-Host "✓ Freed $freed MB of VRAM!" -ForegroundColor Green
    }
}

Write-Host "`nTo restart with optimal model for your 3080 Ti:" -ForegroundColor Cyan
Write-Host "  ollama serve" -ForegroundColor White
Write-Host "  ollama run qwen2.5:7b" -ForegroundColor White
Write-Host ""
