@echo off
REM Download HAK-GAL Knowledge Base

echo Downloading HAK-GAL Knowledge Base (7.1 MB)...
curl -L https://github.com/sookoothaii/HAK-GAL-Hexagonal/releases/download/v2.0.0/hexagonal_kb.db -o hexagonal_kb.db

if exist hexagonal_kb.db (
    echo Knowledge base downloaded successfully!
) else (
    echo Download failed!
    exit /b 1
)
