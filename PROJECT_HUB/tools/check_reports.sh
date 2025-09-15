#!/bin/bash
# HAK_GAL Report Manager - Convenience Script
# Usage: ./check_reports.sh [--live]

echo "================================================"
echo "     HAK_GAL Report Manager v1.0"
echo "     Automated Compliance & SSOT Tool"
echo "================================================"
echo ""

# Set Python path
PYTHON_PATH="python"
SCRIPT_PATH="D:/MCP Mods/HAK_GAL_HEXAGONAL/PROJECT_HUB/tools/report_manager.py"

# Check if --live flag is provided
if [ "$1" == "--live" ]; then
    echo "🔴 LIVE MODE - Changes will be applied!"
    echo "Press Ctrl+C to cancel, or Enter to continue..."
    read
    $PYTHON_PATH "$SCRIPT_PATH" --live
else
    echo "🔵 DRY RUN MODE - No changes will be made"
    echo ""
    $PYTHON_PATH "$SCRIPT_PATH"
    echo ""
    echo "To apply corrections, run: $0 --live"
fi

echo ""
echo "================================================"
echo "Report saved to: PROJECT_HUB/docs/meta/compliance_report.md"
echo "================================================"
