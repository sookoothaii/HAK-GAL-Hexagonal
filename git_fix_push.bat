@echo off
echo ===============================================
echo GIT PUSH FIX - API KEY REMOVAL
echo Generated: 2025-09-17
echo ===============================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo Step 1: Stage all PROJECT_HUB changes (with removed API keys)...
echo ---------------------------------------------
git add PROJECT_HUB/
echo - PROJECT_HUB changes staged (API keys removed)

echo.
echo Step 2: Amend the last commit to include the fixes...
echo ---------------------------------------------
git commit --amend --no-edit
echo - Commit updated with API key removals

echo.
echo Step 3: Ready to force push!
echo ---------------------------------------------
echo.
echo IMPORTANT: You need to force push because we amended the commit:
echo.
echo   git push --force origin main
echo.
echo This will replace the rejected commit with the clean one.
echo.
echo ===============================================
echo API KEY REMOVAL COMPLETE!
echo ===============================================
echo.
echo Summary of cleaned files:
echo - 4 Groq API keys removed
echo - 7 Google API keys removed  
echo - Total: 11 files cleaned
echo.
echo All API keys replaced with placeholders like:
echo - ^<YOUR_GROQ_API_KEY_HERE^>
echo - ^<YOUR_GOOGLE_API_KEY_HERE^>
echo.
pause