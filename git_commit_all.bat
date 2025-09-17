@echo off
echo ===============================================
echo GIT COMMIT SCRIPT FOR HAK_GAL_HEXAGONAL
echo Generated: 2025-09-17
echo ===============================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo Step 1: Adding all important changes...
echo ---------------------------------------------
git add PROJECT_HUB/
echo - PROJECT_HUB changes added

git add .gitignore
echo - .gitignore changes added

git add hexagonal_kb.db
echo - Knowledge base added (38,288 facts)

git add git_cleanup.bat
echo - Cleanup script added

git add git_commit_all.bat
echo - This script added

echo.
echo Step 2: Showing staged changes...
echo ---------------------------------------------
git status --short

echo.
echo Step 3: Creating comprehensive commit...
echo ---------------------------------------------
git commit -m "PROJECT_HUB: Complete reorganization + KB update (38,288 facts)" ^
          -m "- Reorganized 425 markdown documents with 100%% frontmatter coverage" ^
          -m "- Created comprehensive catalog system (catalog_20250917.md/json)" ^
          -m "- Updated knowledge base to 38,288 verified facts" ^
          -m "- Added compliance report and documentation" ^
          -m "- Fixed 4 missing frontmatters (TOOLS_3006/3007/INDEX, cleanup_report)" ^
          -m "- Updated .gitignore for better repo hygiene"

echo.
echo ===============================================
echo COMMIT COMPLETE!
echo ===============================================
echo.
echo Next steps:
echo 1. Review the commit: git log --oneline -1
echo 2. Push to remote:   git push origin main
echo.
pause