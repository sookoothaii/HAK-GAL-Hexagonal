@echo off
echo ========================================
echo HAK_GAL CADDY START SCRIPT
echo ========================================
echo.

echo [1/3] Checking Backend Status...
curl -s http://127.0.0.1:5002/health >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Backend not running on port 5002
    echo Please start Backend first: python src_hexagonal/infrastructure/engines/aethelred_extended_fixed.py
    echo.
) else (
    echo ✅ Backend is running on port 5002
)

echo [2/3] Checking Frontend Status...
curl -s http://127.0.0.1:5173/ >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Frontend not running on port 5173
    echo Please start Frontend first: cd frontend && npm run dev (Port 5173)
    echo.
) else (
    echo ✅ Frontend is running on port 5173
)

echo [3/3] Starting Caddy...
echo Starting Caddy on port 8088...
echo.
echo Caddy will proxy:
echo - Frontend: http://localhost:8088 -> http://127.0.0.1:5173
echo - Backend: http://localhost:8088/api/* -> http://127.0.0.1:5002
echo.
echo Press Ctrl+C to stop Caddy
echo.

caddy.exe run --config Caddyfile
