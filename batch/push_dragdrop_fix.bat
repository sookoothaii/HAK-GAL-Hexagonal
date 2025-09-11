@echo off
echo ========================================
echo Pushing Drag & Drop Fix to GitHub
echo ========================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo Adding changes...
git add frontend/src/components/llm/LLMConfiguration.tsx

echo.
echo Committing...
git commit -m "fix: Add drag & drop functionality to LLM provider chain order" -m "- Added draggable attribute and event handlers" -m "- Visual feedback during drag operations" -m "- Proper reordering logic with order index updates"

echo.
echo Pushing to GitHub...
git push origin HEAD

echo.
echo ========================================
echo Push complete!
echo ========================================
pause
