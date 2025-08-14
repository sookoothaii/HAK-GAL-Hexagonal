@echo off
echo Cleaning Vite cache...
cd /d "D:\MCP Mods\HAK_GAL_SUITE\frontend_new"

echo Stopping any running processes...
taskkill /F /IM node.exe 2>nul

echo Removing Vite cache...
rmdir /s /q node_modules\.vite 2>nul
rmdir /s /q .vite 2>nul

echo Clearing npm cache...
npm cache clean --force

echo Starting frontend...
npm run dev

pause
