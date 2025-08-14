@echo off
REM HAK_GAL MCP - FIX für Config-Fehler
REM =====================================

echo.
echo ========================================
echo HAK_GAL MCP CONFIG FIX
echo ========================================
echo.
echo Der Fehler wurde gefunden:
echo Claude erwartet "command" als STRING, nicht als ARRAY!
echo.

REM Backup der fehlerhaften Config
echo [1/3] Erstelle Backup der fehlerhaften Config...
copy "%APPDATA%\Claude\claude_desktop_config.json" "%APPDATA%\Claude\claude_desktop_config_ERROR.json" >nul 2>&1
echo Backup: claude_desktop_config_ERROR.json

REM Finde Python
echo.
echo [2/3] Suche Python Installation...
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Python gefunden im PATH
    copy "D:\MCP Mods\HAK_GAL_HEXAGONAL\claude_config_FIXED.json" "%APPDATA%\Claude\claude_desktop_config.json" >nul
    echo ✓ Installiere: claude_config_FIXED.json
) else (
    echo ⚠ Python nicht im PATH gefunden
    echo.
    echo Bitte wählen Sie:
    echo [1] Python ist installiert (ich gebe den Pfad an)
    echo [2] Python über 'py' Launcher verwenden
    echo [3] Abbrechen
    echo.
    set /p choice="Ihre Wahl (1/2/3): "
    
    if "!choice!"=="1" (
        set /p pypath="Python.exe Pfad eingeben: "
        echo {"mcpServers":{"hak-gal":{"command":"!pypath!","args":["D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hak_gal_mcp_v2.py"]}}} > "%APPDATA%\Claude\claude_desktop_config.json"
    ) else if "!choice!"=="2" (
        echo {"mcpServers":{"hak-gal":{"command":"py","args":["D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hak_gal_mcp_v2.py"]}}} > "%APPDATA%\Claude\claude_desktop_config.json"
    ) else (
        echo Abgebrochen.
        pause
        exit /b 1
    )
)

echo.
echo [3/3] Config erfolgreich installiert!
echo.
echo ========================================
echo WICHTIG - Nächste Schritte:
echo ========================================
echo.
echo 1. Claude KOMPLETT beenden:
echo    - Schließen Sie alle Claude-Fenster
echo    - System Tray → Rechtsklick auf Claude → Quit
echo    - Task Manager → Prüfen dass kein Claude.exe läuft
echo.
echo 2. Claude neu starten
echo.
echo 3. Testen Sie mit:
echo    "What MCP tools do you have?"
echo.
echo Falls der Fehler weiterhin auftritt:
echo - Öffnen Sie: %APPDATA%\Claude\claude_desktop_config.json
echo - Prüfen Sie die Syntax
echo - Logs: D:\MCP Mods\HAK_GAL_HEXAGONAL\mcp_server_v2.log
echo.
pause
