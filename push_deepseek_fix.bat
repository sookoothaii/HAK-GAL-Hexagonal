@echo off
echo ========================================
echo Pushing DeepSeek Timeout Fix to GitHub
echo ========================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo Adding changes...
git add src_hexagonal/adapters/llm_providers.py

echo.
echo Committing...
git commit -m "fix: Increase DeepSeek timeout and max_tokens" -m "- Increased timeout from 8s to 30s to prevent connection timeouts" -m "- Increased max_tokens from 200 to 1000 for better responses"

echo.
echo Pushing to GitHub...
git push origin HEAD

echo.
echo ========================================
echo Push complete!
echo ========================================
pause
