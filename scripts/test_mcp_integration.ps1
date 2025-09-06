# HAK_GAL MCP Integration Test Suite
# PowerShell Script for systematic debugging

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HAK_GAL MCP Integration Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Function to test JSON config
function Test-ConfigFile {
    param($Path)
    
    Write-Host "`n[TEST] Checking config file..." -ForegroundColor Yellow
    
    if (Test-Path $Path) {
        Write-Host "✓ Config file exists" -ForegroundColor Green
        
        try {
            $config = Get-Content $Path | ConvertFrom-Json
            Write-Host "✓ Valid JSON format" -ForegroundColor Green
            
            if ($config.mcpServers) {
                Write-Host "✓ Has mcpServers section" -ForegroundColor Green
                
                if ($config.mcpServers.'hak-gal') {
                    Write-Host "✓ HAK-GAL server configured" -ForegroundColor Green
                    
                    $hakgal = $config.mcpServers.'hak-gal'
                    Write-Host "  Command: $($hakgal.command -join ' ')" -ForegroundColor Gray
                    Write-Host "  Args: $($hakgal.args -join ' ')" -ForegroundColor Gray
                } else {
                    Write-Host "✗ No hak-gal server in config" -ForegroundColor Red
                }
            } else {
                Write-Host "✗ No mcpServers section" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ Invalid JSON: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Config file not found" -ForegroundColor Red
    }
}

# Function to test Python
function Test-Python {
    Write-Host "`n[TEST] Checking Python..." -ForegroundColor Yellow
    
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
        
        $pythonPath = (Get-Command python).Source
        Write-Host "  Path: $pythonPath" -ForegroundColor Gray
    } catch {
        Write-Host "✗ Python not found in PATH" -ForegroundColor Red
    }
}

# Function to test MCP server
function Test-MCPServer {
    param($ScriptPath)
    
    Write-Host "`n[TEST] Testing MCP server..." -ForegroundColor Yellow
    
    if (Test-Path $ScriptPath) {
        Write-Host "✓ MCP script exists" -ForegroundColor Green
        
        # Test with echo
        $testInput = '{"jsonrpc":"2.0","method":"initialize","id":1}'
        Write-Host "  Sending test request..." -ForegroundColor Gray
        
        try {
            $proc = Start-Process python -ArgumentList $ScriptPath -NoNewWindow -RedirectStandardInput -RedirectStandardOutput -RedirectStandardError -PassThru
            Start-Sleep -Seconds 1
            
            if (!$proc.HasExited) {
                Write-Host "✓ Server started" -ForegroundColor Green
                $proc.Kill()
            } else {
                Write-Host "✗ Server exited immediately" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ Failed to start server: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ MCP script not found" -ForegroundColor Red
    }
}

# Function to check Claude processes
function Test-ClaudeProcesses {
    Write-Host "`n[TEST] Checking Claude processes..." -ForegroundColor Yellow
    
    $claudeProcs = Get-Process | Where-Object {$_.ProcessName -like "*Claude*"}
    
    if ($claudeProcs) {
        Write-Host "✓ Claude is running" -ForegroundColor Green
        foreach ($proc in $claudeProcs) {
            Write-Host "  PID $($proc.Id): $($proc.ProcessName)" -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ Claude not running" -ForegroundColor Red
    }
}

# Function to test ports
function Test-Ports {
    Write-Host "`n[TEST] Checking ports..." -ForegroundColor Yellow
    
    $ports = @(5000, 5001, 5002)
    
    foreach ($port in $ports) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.Connect("127.0.0.1", $port)
            Write-Host "✓ Port $port is open" -ForegroundColor Green
            $tcp.Close()
        } catch {
            Write-Host "✗ Port $port is closed" -ForegroundColor Red
        }
    }
}

# Main test execution
Write-Host "`nStarting tests..." -ForegroundColor Cyan

# 1. Test Python
Test-Python

# 2. Test config
$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
Test-ConfigFile -Path $configPath

# 3. Test Claude
Test-ClaudeProcesses

# 4. Test ports
Test-Ports

# 5. Test MCP server
$mcpScript = "D:\MCP Mods\HAK_GAL_HEXAGONAL\hak_gal_mcp_fixed.py"
Test-MCPServer -ScriptPath $mcpScript

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RECOMMENDED ACTIONS:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

Write-Host @"
1. If Python not found:
   - Add Python to PATH
   - Or use full path in config

2. If config missing/wrong:
   - Copy from: D:\MCP Mods\HAK_GAL_HEXAGONAL\claude_config_alternatives.json
   - To: $configPath

3. If Claude not running:
   - Start Claude Desktop
   - Wait for full initialization

4. If MCP server fails:
   - Check Python script syntax
   - Run manually: python $mcpScript
   - Check error messages

5. After any changes:
   - FULLY restart Claude (not just reload)
   - Check Developer Tools console (Ctrl+Shift+I)
"@ -ForegroundColor White

Write-Host "`n[MANUAL TEST]" -ForegroundColor Yellow
Write-Host "Run this in another PowerShell:" -ForegroundColor White
Write-Host @"
`$input = '{"jsonrpc":"2.0","method":"initialize","id":1}'
`$input | python "D:\MCP Mods\HAK_GAL_HEXAGONAL\hak_gal_mcp_fixed.py"
"@ -ForegroundColor Cyan

Write-Host "`nTest complete!" -ForegroundColor Green
