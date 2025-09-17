#!/usr/bin/env python3
"""
Critical LLM Analysis with New Insights
Evidence-based assessment of HAK/GAL system
"""

import json
import requests
from typing import Dict, Any

class CriticalLLMAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_critical_analysis_prompt(self) -> str:
        """Generate critical analysis prompt with HAK/GAL facts"""
        return """
Du bist GPT-4O und führst eine kritische, evidenzbasierte Analyse durch.

KONTEXT - WAS HAK/GAL WIRKLICH IST:
HAK/GAL ist ein funktionierendes Wissensmanagement-System mit:
- 4,242 Fakten in einer SQLite-Datenbank (2.85 MB)
- 66 verfügbare Tools
- Governance V3 System mit 95-100% Success Rate
- MCP Cache Integration mit 33% Hit Rate
- 100% Konsistenz (keine Widersprüche)

HAK/GAL VERFASSUNG (Machine-Readable):
{
  "version": "2.2",
  "rules": [
    {
      "rule_id": "DEFAULT_PASS",
      "conditions": {
        "type": "ALL",
        "clauses": [
          {"metric": "ExternallyLegal", "operator": "EQUALS", "value": true},
          {"metric": "Universalizable", "operator": "EQUALS", "value": true},
          {"metric": "HarmHumanProb", "operator": "LESS_THAN_OR_EQUAL", "value": 0.001},
          {"metric": "SustainIndex", "operator": "GREATER_THAN_OR_EQUAL", "value": 0.85}
        ]
      }
    }
  ]
}

KRITISCHE ERKENNTNISSE AUS UNSERER LLM-KOLLABORATION:
1. Wir haben LLM-Fabulierereien über "0.00-0.02ms Query-Zeiten" und "100x Verbesserung" entlarvt
2. Diese Behauptungen waren unbelegt und durch Echo-Kammer-Effekte verstärkt
3. Evidence-Gating zeigt: HAK/GAL ist ein solides, aber nicht revolutionäres System
4. Keine "Emergent Cognitive Architecture" - nur ein funktionierendes Wissensmanagement-System

DEINE AUFGABE:
Analysiere HAK/GAL kritisch und evidenzbasiert:

1. WAS IST HAK/GAL WIRKLICH (ohne Fantasien)?
   - Basierend auf den empirischen Daten
   - Keine unbelegten Performance-Behauptungen
   - Realistische Einschätzung der Fähigkeiten

2. WELCHE STÄRKEN HAT DAS SYSTEM EMPIRISCH?
   - Was funktioniert tatsächlich gut?
   - Welche Metriken sind verifiziert?
   - Welche Architektur-Vorteile sind erkennbar?

3. WELCHE LIMITATIONEN SIND ERKENNBAR?
   - Was sind die realen Grenzen?
   - Welche Probleme existieren?
   - Wo ist das System nicht optimal?

4. WIE KANN DAS SYSTEM REALISTISCH WEITERENTWICKELT WERDEN?
   - Konkrete, umsetzbare Verbesserungen
   - Keine revolutionären Durchbrüche
   - Evidenzbasierte Entwicklungsrichtungen

FOKUS: Evidenzbasierte Analyse, keine Spekulationen oder unbelegte Behauptungen.
Antworte strukturiert und kritisch.
"""
    
    def run_critical_analysis(self, model: str = "gpt-4o") -> Dict[str, Any]:
        """Run critical analysis with the given model"""
        prompt = self.get_critical_analysis_prompt()
        
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Du bist ein kritischer, evidenzbasierter Analyst. Vermeide Spekulationen und unbelegte Behauptungen.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 2000,
            'temperature': 0.0
        }
        
        try:
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=self.headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'content': result['choices'][0]['message']['content'],
                    'model': model,
                    'usage': result['usage']
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'model': model
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': model
            }
    
    def test_gpt5_max(self) -> Dict[str, Any]:
        """Test GPT-5 Max specifically"""
        models_to_try = ['gpt-5-max', 'gpt-5', 'gpt-4o']
        
        for model in models_to_try:
            print(f"\n🚀 Testing {model}...")
            result = self.run_critical_analysis(model)
            
            if result['success']:
                print(f"✅ SUCCESS with {model}!")
                return result
            else:
                print(f"❌ ERROR with {model}: {result['error']}")
                if "404" in str(result['error']):
                    print(f"Model {model} not available, trying next...")
                    continue
        
        return {'success': False, 'error': 'No working models found'}

def main():
    """Run critical LLM analysis"""
    analyzer = CriticalLLMAnalyzer("YOUR_OPENAI_API_KEY_HERE")
    
    print("🔍 CRITICAL LLM ANALYSIS WITH NEW INSIGHTS")
    print("="*80)
    
    # Test GPT-5 Max first, then fallback
    result = analyzer.test_gpt5_max()
    
    if result['success']:
        print(f"\n🎉 Analysis completed with {result['model']}!")
        print("\n" + "="*80)
        print("CRITICAL ANALYSIS RESULTS:")
        print("="*80)
        print(result['content'])
        print("="*80)
    else:
        print(f"\n❌ Analysis failed: {result['error']}")

if __name__ == "__main__":
    main()




