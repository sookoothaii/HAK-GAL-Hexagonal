"""
Test des finalen Quality Analysis Fixes
"""

import requests
import json

API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
BASE_URL = "http://127.0.0.1:5002/api/hallucination-prevention"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

print("=== Testing Fixed Quality Analysis ===\n")

# Server muss neu gestartet werden für den SQL-Fix
print("HINWEIS: Server muss nach dem SQL-Fix neu gestartet werden!\n")

response = requests.post(
    f"{BASE_URL}/quality-analysis",
    headers=HEADERS,
    json={}
)

if response.status_code == 200:
    data = response.json()
    
    if data.get('success') and 'analysis' in data:
        analysis = data['analysis']
        
        print("✅ Quality Analysis Response:")
        print(f"   Success: {analysis.get('success')}")
        print(f"   Total Facts: {analysis.get('total_facts')}")
        print(f"   HasProperty Count: {analysis.get('hasproperty_count')}")
        print(f"   HasProperty Percent: {analysis.get('hasproperty_percent')}%")
        print(f"   Mock Data: {analysis.get('mock_data')}")
        print(f"   Data Source: {analysis.get('data_source')}")
        
        if 'predicates' in analysis:
            print("\n   Prädikat-Verteilung:")
            for pred, count in analysis['predicates'].items():
                print(f"     {pred}: {count}")
        
        if 'domain_distribution' in analysis:
            print("\n   Domain-Verteilung:")
            for domain, count in analysis['domain_distribution'].items():
                if count > 0:
                    print(f"     {domain}: {count}")
        
        if 'quality_metrics' in analysis:
            print("\n   Quality Metrics:")
            for metric, value in analysis['quality_metrics'].items():
                print(f"     {metric}: {value:.1f}%")
        
        # Check success criteria
        if (analysis.get('mock_data') == False and 
            analysis.get('hasproperty_count') != 29499 and
            analysis.get('data_source') == 'real_database_analysis'):
            print("\n✅ ERFOLG: Quality Analysis liefert echte Daten ohne Mocks!")
        else:
            print("\n❌ FEHLER: Immer noch Mock-Daten oder andere Probleme")
    else:
        print("❌ Analyse fehlgeschlagen oder keine Daten")
        print(f"Response: {json.dumps(data, indent=2)}")
else:
    print(f"❌ HTTP Error: {response.status_code}")
    print(f"Response: {response.text}")

# Führe auch die komplette Test-Suite nochmal aus
print("\n" + "="*60)
print("Führe komplette Test-Suite aus...")
print("="*60)

import subprocess
result = subprocess.run(
    ['python', 'D:/MCP Mods/HAK_GAL_HEXAGONAL/test_hallucination_prevention_fixes.py'],
    capture_output=True,
    text=True,
    encoding='utf-8'
)

# Zeige nur die Zusammenfassung
lines = result.stdout.split('\n')
summary_started = False
for line in lines:
    if "ZUSAMMENFASSUNG" in line:
        summary_started = True
    if summary_started:
        print(line)
