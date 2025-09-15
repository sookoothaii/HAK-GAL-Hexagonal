---
title: "HAK_GAL Report Manager - User Guide"
created: "2025-09-15T17:00:00Z"
author: "claude-opus-4.1"
topics: ["guides"]
tags: ["tools", "automation", "compliance", "ssot", "report-management"]
privacy: "internal"
summary_200: |-
  Comprehensive guide for the HAK_GAL Report Manager tool that automates compliance checking,
  report validation, and SSOT (Single Source of Truth) registry management. Includes automatic
  correction of common issues, file relocation, security scanning, and frontmatter validation.
  Essential tool for maintaining documentation quality and preventing LLM-generated errors.
---

# HAK_GAL Report Manager - User Guide

## Overview

The **HAK_GAL Report Manager** (`report_manager.py`) is a comprehensive Python tool that automates the management and compliance checking of technical reports in the HAK_GAL system.

## Key Features

### 1. **Automated Compliance Checking**
- Validates all markdown files against HAK_GAL standards
- Checks frontmatter completeness (7 required fields)
- Verifies correct API syntax (`hak-gal.` not `hak-gal:`)
- Detects exposed authentication tokens
- Validates date formats and logic
- Ensures correct file placement

### 2. **Single Source of Truth (SSOT) Registry**
- Creates centralized registry of all technical reports
- Tracks metadata, compliance scores, and issues
- Maintains file hashes for change detection
- JSON-based persistent storage

### 3. **Automatic Error Correction**
- Fixes common API syntax errors
- Replaces exposed tokens with placeholders
- Adds missing frontmatter
- Corrects function names
- Updates incorrect dates

### 4. **File Relocation**
- Moves misplaced files to correct directories
- Follows PH-LIP routing rules
- Updates references automatically

### 5. **Comprehensive Reporting**
- Generates detailed compliance reports
- Tracks statistics and trends
- Provides actionable recommendations

## Installation

```bash
# Install required dependencies
pip install pyyaml

# Navigate to tools directory
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\tools"
```

## Usage

### Basic Scan (Dry Run)
```bash
# Scan all files without making changes
python report_manager.py
```

### Live Mode (Apply Corrections)
```bash
# Actually apply corrections and relocations
python report_manager.py --live
```

### Custom Output
```bash
# Specify output report location
python report_manager.py --output my_compliance_report.md
```

## What It Checks

### Security Issues (CRITICAL)
- Exposed authentication tokens
- Hardcoded credentials
- Sensitive information in plaintext

### Frontmatter Compliance (HIGH)
- All 7 required fields present
- Correct data types (arrays vs strings)
- Summary word count ≤ 200
- Valid YAML syntax

### API Syntax (HIGH)
- Correct tool invocation syntax
- Valid function names
- Proper parameter formats

### Date Issues (MEDIUM)
- Dates not in future
- Correct ISO format
- No legacy date confusion

### File Location (HIGH)
- Files in correct directories per routing rules
- No unauthorized root-level files
- Proper topic-based organization

## SSOT Registry Structure

The tool creates a centralized registry at:
`PROJECT_HUB/docs/meta/TECHNICAL_REPORTS_SSOT.json`

Registry entry example:
```json
{
  "PROJECT_HUB/docs/technical_reports/REPORT.md": {
    "file_path": "...",
    "title": "Technical Report",
    "created": "2025-09-15T12:00:00Z",
    "author": "claude-opus-4.1",
    "topics": ["technical_reports"],
    "tags": ["analysis", "performance"],
    "privacy": "internal",
    "summary_200": "...",
    "file_hash": "sha256_hash",
    "last_validated": "2025-09-15T17:00:00Z",
    "compliance_score": 85.0,
    "issues": ["MEDIUM: Missing field: tags"],
    "corrections_applied": ["Fixed API syntax"]
  }
}
```

## Compliance Scoring

Scores are calculated based on issue severity:
- **CRITICAL issues**: -25 points each
- **HIGH issues**: -15 points each
- **MEDIUM issues**: -10 points each
- **LOW issues**: -5 points each

Perfect compliance = 100 points

## Common Issues It Fixes

### 1. Token Exposure
**Before:** `auth_token="a7b3d4e9f2c8a1d6b5e3f9c4a2d7b1e8f3a9c5d2b6e4a8c1f7d3b9e5a2c6d4f8"`
**After:** `auth_token="<YOUR_TOKEN_HERE>"`

### 2. Wrong API Syntax
**Before:** `hak-gal:kb_stats()`
**After:** `hak-gal.kb_stats()`

### 3. Deprecated Functions
**Before:** `list_directory(path="...")`
**After:** `list_files(path="...")`

### 4. Missing Frontmatter
Automatically adds complete frontmatter with:
- Current timestamp
- Inferred topic from path
- Auto-generated title
- Placeholder summary

### 5. Wrong File Location
**Before:** `D:\MCP Mods\HAK_GAL_HEXAGONAL\REPORT.md`
**After:** `D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\docs\technical_reports\REPORT.md`

## Routing Rules (PH-LIP)

The tool follows these routing rules:
- `topics: ["guides"]` → `docs/guides/`
- `topics: ["meta"]` → `docs/meta/`
- `topics: ["system"]` → `docs/system/`
- `topics: ["technical_reports"]` → `docs/technical_reports/`
- `topics: ["mcp"]` → `docs/mcp/`
- `topics: ["analysis"]` → `analysis/`

## Best Practices

### Before Running
1. **Backup important files** - The tool can modify many files
2. **Run dry-run first** - Check what will be changed
3. **Review the report** - Understand issues before fixing

### After Running
1. **Review corrections** - Ensure auto-fixes are appropriate
2. **Update references** - If files were relocated
3. **Commit changes** - Track modifications in version control
4. **Rotate tokens** - If any were exposed

## Integration with LLM Workflow

### For New LLM Sessions
```python
# At session start
python report_manager.py  # Check current state

# After LLM work
python report_manager.py --live  # Fix any issues introduced
```

### For Validation
```python
# Validate specific report
from report_manager import ComplianceChecker
checker = ComplianceChecker()
issues = checker.check_file(Path("my_report.md"))
```

## Troubleshooting

### "Database is locked"
- Close any applications accessing the SQLite database
- Wait a moment and retry

### "Permission denied"
- Run with appropriate file system permissions
- Check file isn't open in another application

### "YAML parse error"
- Manually fix malformed frontmatter
- Ensure proper indentation

## Example Output

```
=====================================
SCAN COMPLETE
=====================================
Total Files: 127
Compliant: 89
Issues: 234 (12 critical)
Corrections: 156
Relocations: 8

Full report: PROJECT_HUB/docs/meta/compliance_report.md

⚠️  This was a DRY RUN - no changes were made
Run with --live to apply corrections
```

## Future Enhancements

Planned features:
- Git integration for automatic commits
- Webhook notifications for critical issues
- Dashboard visualization
- Custom rule definitions
- Incremental scanning
- Multi-language support

## Support

For issues or questions:
1. Check the compliance report for details
2. Review this guide
3. Examine the source code comments
4. Consult the HAK_GAL Constitution

---

*This tool is essential for maintaining documentation quality and preventing accumulation of LLM-generated errors.*
