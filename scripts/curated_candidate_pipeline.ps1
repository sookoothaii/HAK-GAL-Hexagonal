<#
Curated Candidate Pipeline (safe, no KB writes)
- Step 1: auto_topics_from_kb.py -> PROJECT_HUB/topics.txt (Top-Entitäten)
- Step 2: generate_candidates_from_topics.py -> PROJECT_HUB/reports/candidates_<ts>.md (Review-Checkliste)
- Step 3: Hinweis zum manuellen Approve (MCP/REST) mit Kontextquelle
#>
param(
  [int]$Limit = 5000
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
cd $here\..

if (-not (Test-Path .\.venv_hexa\Scripts\Activate.ps1)) {
  Write-Host "venv not found" -ForegroundColor Yellow
  exit 1
}
. .\.venv_hexa\Scripts\Activate.ps1

Write-Host "[1/2] Generating topics from KB..." -ForegroundColor Cyan
.\.venv_hexa\Scripts\python.exe scripts\auto_topics_from_kb.py --limit $Limit

Write-Host "[2/2] Generating candidates (review-first)..." -ForegroundColor Cyan
.\.venv_hexa\Scripts\python.exe scripts\generate_candidates_from_topics.py

Write-Host "Done. Review candidates in PROJECT_HUB/reports and approve selected facts via MCP/REST with context source 'human_verified'." -ForegroundColor Green
