@echo off
REM ====================================
REM PROJECT_HUB Cleanup Script - FINAL
REM Entfernt ALLE alten Snapshots
REM Behält nur den finalen Clean-Snapshot
REM ====================================

echo ======================================
echo PROJECT_HUB FINAL CLEANUP
echo ======================================
echo.
echo Entferne ALLE alten Snapshots...
echo Behalte nur: snapshot_20250813_214057 (FINALE ÜBERGABE)
echo.

REM ALLE alten Snapshots entfernen
echo [1/7] Entferne snapshot_20250813_213850...
rmdir /S /Q "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\snapshot_20250813_213850" 2>nul

echo [2/7] Entferne snapshot_20250813_213335...
rmdir /S /Q "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\snapshot_20250813_213335" 2>nul

echo [3/7] Entferne snapshot_20250813_211917...
rmdir /S /Q "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\snapshot_20250813_211917" 2>nul

echo [4/7] Entferne snapshot_20250813_210229...
rmdir /S /Q "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\snapshot_20250813_210229" 2>nul

echo [5/7] Entferne snapshot_20250813_204605...
rmdir /S /Q "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\snapshot_20250813_204605" 2>nul

echo [6/7] Entferne snapshot_20250813_204100...
rmdir /S /Q "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\snapshot_20250813_204100" 2>nul

echo [7/7] Entferne snapshot_20250813_202044...
rmdir /S /Q "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\snapshot_20250813_202044" 2>nul

echo.
echo ======================================
echo ✅ CLEANUP ABGESCHLOSSEN!
echo ======================================
echo.
echo Verbleibende Dateien im PROJECT_HUB:
echo --------------------------------------
dir /B "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\" 2>nul
echo.
echo ======================================
echo SYSTEM STATUS:
echo ======================================
echo.
if exist "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\SESSION_INIT_PROTOCOL.md" (
    echo ✅ SESSION_INIT_PROTOCOL.md vorhanden
) else (
    echo ❌ SESSION_INIT_PROTOCOL.md FEHLT!
)

if exist "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\snapshot_20250813_214057" (
    echo ✅ Finaler Snapshot vorhanden
) else (
    echo ❌ Finaler Snapshot FEHLT!
)

echo.
echo ======================================
echo NEUE INSTANZ braucht nur noch:
echo ======================================
echo.
echo Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB\\SESSION_INIT_PROTOCOL.md'
echo.
echo Das war's! System ist vollständig selbst-dokumentiert.
echo.
pause
