#!/usr/bin/env python3
"""
HAK-GAL Scripts Audit Report
Erstellt: 2025-09-22
Zweck: Analyse und Empfehlungen für 410 Python-Skripte
"""

import os
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path

def analyze_scripts():
    scripts_dir = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts")
    
    # Sammle alle Python-Dateien
    py_files = list(scripts_dir.glob("*.py"))
    
    results = {
        'total': len(py_files),
        'critical': [],
        'consolidate': defaultdict(list),
        'archive': [],
        'delete': []
    }
    
    # Kritische System-Dateien
    critical_patterns = [
        r'hak_gal_mcp.*\.py$',
        r'hexagonal_.*\.py$',
        r'start_.*\.py$',
        r'server.*\.py$',
        r'api.*\.py$'
    ]
    
    # Zu löschende Muster
    delete_patterns = [
        r'.*_old\.py$',
        r'.*_backup\.py$',
        r'.*_temp\.py$',
        r'.*_DEPRECATED\.py$',
        r'test_.*_debug\.py$'
    ]
    
    for file in py_files:
        filename = file.name
        
        # Kritische Dateien
        if any(re.search(pat, filename) for pat in critical_patterns):
            results['critical'].append(filename)
            continue
            
        # Zu löschende Dateien
        if any(re.search(pat, filename) for pat in delete_patterns):
            results['delete'].append(filename)
            continue
            
        # Duplikate finden
        base = re.sub(r'(_fixed|_v\d+|_new|_improved|_real)', '', filename)
        if base != filename:  # Hat Suffix
            results['consolidate'][base].append(filename)
            continue
            
        # Alte Tests archivieren
        if filename.startswith('test_'):
            age_days = (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).days
            if age_days > 7:
                results['archive'].append((filename, age_days))
    
    return results

def generate_report():
    results = analyze_scripts()
    
    report = []
    report.append("# HAK-GAL SCRIPTS AUDIT REPORT")
    report.append(f"\nDatum: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"Analysierte Dateien: {results['total']}")
    
    report.append("\n## ZUSAMMENFASSUNG")
    report.append(f"- Kritische Systemdateien: {len(results['critical'])}")
    report.append(f"- Zu konsolidierende Gruppen: {len(results['consolidate'])}")
    report.append(f"- Zu archivierende Tests: {len(results['archive'])}")
    report.append(f"- Zu löschende Dateien: {len(results['delete'])}")
    
    report.append("\n## KRITISCHE SYSTEMDATEIEN (BEHALTEN)")
    for f in sorted(results['critical'])[:20]:
        report.append(f"- {f}")
    
    report.append("\n## ZU KONSOLIDIERENDE DUPLIKATE")
    for base, variants in sorted(results['consolidate'].items())[:10]:
        report.append(f"\n### {base}")
        for v in variants:
            report.append(f"  - {v}")
    
    report.append("\n## EMPFOHLENE NEUE STRUKTUR")
    report.append("""
    scripts/
    ├── core/              # Systemkern (MCP-Server, API, Governance)
    ├── engines/           # Fact-Generierung (Aethelred, Thesis)
    ├── analysis/          # Analyse-Tools
    ├── maintenance/       # Wartungs-Skripte
    ├── tests/             # Aktive Tests (<7 Tage)
    └── _archive/          # Alte Versionen (Referenz)
    """)
    
    # Geschätzte Einsparung
    keep_count = len(results['critical']) + len(results['consolidate'])
    reduction = (results['total'] - keep_count) * 100 // results['total']
    
    report.append(f"\n## POTENZIELLE REDUKTION")
    report.append(f"Von {results['total']} auf ~{keep_count} Dateien ({reduction}% Reduktion)")
    
    return '\n'.join(report)

if __name__ == "__main__":
    report = generate_report()
    print(report)
    
    # Speichere Report
    report_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\AUDIT_REPORT.md")
    report_path.write_text(report, encoding='utf-8')
    print(f"\n\nReport gespeichert: {report_path}")
