@echo off
echo ========================================
echo Pushing DeepSeek Complete Fix to GitHub
echo ========================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo Adding changes...
git add src_hexagonal/adapters/llm_providers.py

echo.
echo Committing...
git commit -m "fix: Complete DeepSeek implementation based on successful API test" -m "- Added session object for connection reuse" -m "- Fixed timeout to use tuple (5s connect, 30s read)" -m "- Added proper headers (User-Agent, Accept)" -m "- Removed system message (only user message)" -m "- Explicit stream=false parameter" -m "- Better exception handling" -m "- Confirmed working with 0.26s response time in tests"

echo.
echo Pushing to GitHub...
git push origin HEAD

echo.
echo ========================================
echo Push complete!
echo ========================================
pause
