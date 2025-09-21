@echo off
echo ========================================
echo DNS PROBLEM FIXER FOR HAK_GAL
echo ========================================
echo.

echo [1] Flushing DNS Cache...
ipconfig /flushdns
echo.

echo [2] Resetting Winsock...
netsh winsock reset
echo.

echo [3] Setting Google DNS (requires admin)...
netsh interface ip set dns "WLAN" static 8.8.8.8 primary
netsh interface ip add dns "WLAN" 8.8.4.4 index=2
echo.

echo [4] Testing DNS Resolution...
nslookup api.anthropic.com 8.8.8.8
echo.

echo ========================================
echo DNS FIX COMPLETE - Restart Backend Now
echo ========================================
pause
