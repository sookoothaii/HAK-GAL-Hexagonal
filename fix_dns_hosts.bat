@echo off
echo Adding API hosts to Windows hosts file...
echo.
echo This requires Administrator privileges!
echo.

:: Add API hostnames with their IPs
echo 104.18.40.98    api.groq.com >> C:\Windows\System32\drivers\etc\hosts
echo 104.18.26.90    api.deepseek.com >> C:\Windows\System32\drivers\etc\hosts
echo 142.250.185.74  generativelanguage.googleapis.com >> C:\Windows\System32\drivers\etc\hosts

echo.
echo Done! Added:
echo   104.18.40.98    api.groq.com
echo   104.18.26.90    api.deepseek.com  
echo   142.250.185.74  generativelanguage.googleapis.com
echo.
echo Flushing DNS cache...
ipconfig /flushdns

echo.
echo Complete! Restart your HAK_GAL backend now.
pause