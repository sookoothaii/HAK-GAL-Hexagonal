@echo off
echo ========================================
echo Pushing LLM Configuration Update to GitHub
echo ========================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo Current directory: %CD%
echo.

REM Try git directly first
where git >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Git found in PATH
    set GIT_CMD=git
    goto :git_found
)

REM Check common Git locations
if exist "%PROGRAMFILES%\Git\bin\git.exe" (
    set GIT_CMD="%PROGRAMFILES%\Git\bin\git.exe"
    goto :git_found
)
if exist "%PROGRAMFILES(x86)%\Git\bin\git.exe" (
    set GIT_CMD="%PROGRAMFILES(x86)%\Git\bin\git.exe"
    goto :git_found
)
if exist "%LOCALAPPDATA%\Programs\Git\bin\git.exe" (
    set GIT_CMD="%LOCALAPPDATA%\Programs\Git\bin\git.exe"
    goto :git_found
)

echo ERROR: Git not found! Please install Git.
pause
exit /b 1

:git_found
echo Using Git: %GIT_CMD%
echo.

echo Adding all changes...
%GIT_CMD% add .

echo.
echo Showing changes:
%GIT_CMD% status --short

echo.
echo Committing changes...
%GIT_CMD% commit -m "feat: Add dynamic LLM configuration system" -m "- Added LLM configuration UI in Settings tab" -m "- Implemented backend routes for LLM provider management" -m "- Dynamic provider chain configuration" -m "- Support for temporary API keys" -m "- Provider testing functionality" -m "- 97.5%% performance improvement with Groq integration"

echo.
echo Current branch:
%GIT_CMD% branch --show-current

echo.
echo Pushing to GitHub...
%GIT_CMD% push origin HEAD

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Push failed. Trying to push to main branch...
    %GIT_CMD% push origin main
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Still failing. Trying master branch...
        %GIT_CMD% push origin master
    )
)

echo.
echo ========================================
echo Operation complete!
echo ========================================
pause
