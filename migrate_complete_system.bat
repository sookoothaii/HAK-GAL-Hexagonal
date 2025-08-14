@echo off
echo ============================================================
echo HEXAGONAL COMPLETE SYSTEM MIGRATION
echo ============================================================
echo.
echo This script will:
echo 1. Copy frontend from HAK_GAL_SUITE to HEXAGONAL
echo 2. Create proper hexagonal directory structure
echo 3. Configure frontend for HEXAGONAL backend (port 5001)
echo.
echo Press Ctrl+C to cancel or any key to continue...
pause >nul

echo.
echo [1/5] Creating hexagonal directory structure...
if not exist "frontend" mkdir "frontend"
if not exist "docs" mkdir "docs"
if not exist "tests" mkdir "tests"
if not exist "tests\unit" mkdir "tests\unit"
if not exist "tests\integration" mkdir "tests\integration"
if not exist "tests\e2e" mkdir "tests\e2e"
if not exist "scripts" mkdir "scripts"
if not exist "scripts\migration" mkdir "scripts\migration"
if not exist "scripts\maintenance" mkdir "scripts\maintenance"
if not exist "src_hexagonal\infrastructure\database" mkdir "src_hexagonal\infrastructure\database"
if not exist "src_hexagonal\infrastructure\llm" mkdir "src_hexagonal\infrastructure\llm"
if not exist "src_hexagonal\infrastructure\monitoring" mkdir "src_hexagonal\infrastructure\monitoring"
if not exist "config" mkdir "config"
if not exist "data" mkdir "data"
if not exist "logs" mkdir "logs"

echo.
echo [2/5] Copying frontend from HAK_GAL_SUITE...
xcopy /E /I /Y "..\HAK_GAL_SUITE\frontend_new\*" "frontend\"

echo.
echo [3/5] Copying database and knowledge base...
if exist "..\HAK_GAL_SUITE\k_assistant.db" (
    copy /Y "..\HAK_GAL_SUITE\k_assistant.db" "data\k_assistant.db"
    echo Database copied to data\k_assistant.db
)
if exist "..\HAK_GAL_SUITE\k_assistant.kb.jsonl" (
    copy /Y "..\HAK_GAL_SUITE\k_assistant.kb.jsonl" "data\k_assistant.kb.jsonl"
    echo Knowledge base copied to data\k_assistant.kb.jsonl
)

echo.
echo [4/5] Copying configuration files...
if exist "..\HAK_GAL_SUITE\.env" (
    copy /Y "..\HAK_GAL_SUITE\.env" ".env"
    echo Environment variables copied
)

echo.
echo [5/5] Updating frontend configuration for HEXAGONAL...
echo Please run 'update_frontend_config.py' after this script completes

echo.
echo ============================================================
echo MIGRATION STRUCTURE CREATED
echo ============================================================
echo.
echo Next steps:
echo 1. Run: python update_frontend_config.py
echo 2. Install frontend dependencies: cd frontend && npm install
echo 3. Start HEXAGONAL backend: python src_hexagonal\hexagonal_api_enhanced_clean.py
echo 4. Start frontend: cd frontend && npm run dev
echo.
echo Directory structure:
echo HAK_GAL_HEXAGONAL\
echo ├── frontend\              [React/Vite Frontend]
echo ├── src_hexagonal\         [Backend Core]
echo │   ├── core\             [Domain Logic]
echo │   ├── application\      [Use Cases]
echo │   ├── adapters\         [Ports and Adapters]
echo │   └── infrastructure\   [External Systems]
echo │       ├── engines\      [Learning Engines]
echo │       ├── database\     [SQLite/Knowledge Base]
echo │       ├── llm\         [LLM Providers]
echo │       └── monitoring\   [Sentry/Logging]
echo ├── tests\                [Test Suites]
echo ├── scripts\              [Utility Scripts]
echo ├── config\               [Configuration]
echo ├── data\                 [Database Files]
echo └── logs\                 [System Logs]
echo.
pause
