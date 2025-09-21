@echo off
echo ====================================
echo DNS FIX für HAK_GAL LLM Providers
echo ====================================
echo.

echo 1. Flushing DNS Cache...
ipconfig /flushdns
echo.

echo 2. Resetting Winsock...
netsh winsock reset
echo.

echo 3. Testing DNS resolution...
nslookup api.groq.com 8.8.8.8
nslookup api.deepseek.com 8.8.8.8
echo.

echo 4. Setting Google DNS as primary...
echo Run this in elevated PowerShell:
echo netsh interface ip set dns "Ethernet" static 8.8.8.8
echo netsh interface ip add dns "Ethernet" 8.8.4.4 index=2
echo.

echo 5. Alternative: Add to hosts file (C:\Windows\System32\drivers\etc\hosts):
echo # HAK_GAL LLM APIs
echo 104.18.40.98    api.groq.com
echo 104.18.41.98    api.groq.com
echo 104.18.26.90    api.deepseek.com
echo 104.18.27.90    api.deepseek.com
echo.

pause