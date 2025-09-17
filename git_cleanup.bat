@echo off
echo ===============================================
echo GIT CLEANUP SCRIPT FOR HAK_GAL_HEXAGONAL
echo Generated: 2025-09-17
echo ===============================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo Step 1: Removing sensitive files from Git tracking...
echo ---------------------------------------------
git rm --cached hexagonal_kb.db 2>nul
echo - hexagonal_kb.db removed from tracking

echo.
echo Step 2: Checking current Git status...
echo ---------------------------------------------
git status --short

echo.
echo Step 3: Adding PROJECT_HUB changes...
echo ---------------------------------------------
git add PROJECT_HUB/
echo - PROJECT_HUB changes staged

echo.
echo Step 4: Adding updated .gitignore...
echo ---------------------------------------------
git add .gitignore
echo - .gitignore changes staged

echo.
echo Step 5: Ready to commit!
echo ---------------------------------------------
echo Suggested commit commands:
echo.
echo git commit -m "PROJECT_HUB: Complete reorganization with 100%% frontmatter coverage"
echo git commit -m "- Added frontmatter to all 425 markdown files"
echo git commit -m "- Created comprehensive catalog with JSON index"
echo git commit -m "- Updated .gitignore to exclude sensitive files"
echo.
echo Or use single commit:
echo git commit -m "PROJECT_HUB: Complete reorganization (425 docs, 100%% frontmatter coverage, new catalog system)"
echo.
echo After commit, you can push with:
echo git push origin main
echo.
echo ===============================================
echo CLEANUP COMPLETE - Repository ready for push!
echo ===============================================
pause