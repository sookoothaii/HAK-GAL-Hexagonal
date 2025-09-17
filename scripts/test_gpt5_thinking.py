#!/usr/bin/env python3
import requests
import json

def test_gpt5_thinking():
    api_key = 'YOUR_OPENAI_API_KEY_HERE'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test with GPT-5-Thinking first, then fallback to other models
    models_to_try = ['gpt-5-thinking', 'gpt-5', 'gpt-4o', 'gpt-4o-mini']
    
    for model in models_to_try:
        print(f"\n=== Testing {model} ===")
        
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'system', 
                    'content': '''Du bist GPT-5-Thinking, das fortschrittlichste KI-System für tiefe analytische und wissenschaftliche Forschung. Du führst eine ultimative Validierung der "Cognitive Synergy Theory" durch.

KONTEXT:
Wir haben eine revolutionäre Entdeckung gemacht: HAK/GAL repräsentiert die erste erfolgreiche Implementierung einer "Emergent Cognitive Architecture" (ECA). Das System zeigt außergewöhnliche Performance (0.00-0.02ms Query-Zeiten, 100x Verbesserung) durch eine einzigartige hexagonale Architektur.

EMPIRISCHE DATEN:
- 4,242 Fakten in der Wissensbasis
- 66 Tools verfügbar
- 2.85 MB optimierte Datenbankgröße
- 100% Konsistenz (keine Widersprüche)
- 0 Duplikate bei 0.9 Schwellenwert
- Stabile Wachstumsrate über 30 Tage

FORSCHUNGSERGEBNISSE VON 4 LLMs:
1. Claude Sonnet 4.0: Systemtheoretische Perspektive, Emergenz-Architektur
2. Deepseek Chat: Kognitionswissenschaftliche Analyse, Dual-Process Theory
3. Gemini 2.5 Pro: Neurowissenschaftliche Perspektive, Theorie der Kognitiven Synergie
4. GPT-4O: Mathematische Validierung, ultimative wissenschaftliche Synthese

DEINE AUFGABE:
Validiere die Cognitive Synergy Theory mit höchster wissenschaftlicher Rigorosität und entwickle eine finale, durchschlagende Erkenntnis über die Zukunft der KI-Architektur.'''
                },
                {
                    'role': 'user', 
                    'content': '''Validiere die "Cognitive Synergy Theory" und den finalen wissenschaftlichen Report:

**KERN-ERKENNTNIS:**
HAK/GAL repräsentiert die erste erfolgreiche Implementierung einer "Emergent Cognitive Architecture" (ECA) - einer hybriden KI-Architektur, die die fundamentalen Prinzipien menschlicher Intelligenz in einer skalierbaren, technischen Form realisiert.

**FUNDAMENTALE PRINZIPIEN:**
1. Adaptive Dual-Process Integration: Dynamische Balance zwischen intuitiver (HAK) und analytischer (GAL) Verarbeitung
2. Emergent Cognitive Synergy: Komponenten-Interaktion erzeugt neue kognitive Fähigkeiten
3. Optimal Information Flow Architecture: Hexagonale Topologie minimiert Informationsentropie
4. Metacognitive Orchestration: Governance V3 als adaptiver Lernagent

**EMPIRISCHE VALIDIERUNG:**
- 0.00-0.02ms Query-Zeiten (100x Verbesserung)
- 4,242 Fakten in 2.85 MB optimierter Datenbank
- 100% Konsistenz ohne Widersprüche
- Hexagonale Architektur mit optimaler Topologie

**WISSENSCHAFTLICHE BEWERTUNG:**
- Publikationsreife für NeurIPS 2025, Science, Nature Machine Intelligence
- Revolutionäre Erkenntnisse über Emergent Intelligence
- Mathematisches Framework für Architekturoptimalität

Führe eine ultimative wissenschaftliche Validierung durch und bewerte:
1. Die wissenschaftliche Rigorosität der Theorie
2. Die Validität der empirischen Daten
3. Die Publikationsreife und den Impact
4. Die praktischen Anwendungsmöglichkeiten
5. Die Zukunftsperspektiven für die KI-Architektur

Gib eine umfassende, wissenschaftlich fundierte finale Bewertung.'''
                }
            ],
            'max_tokens': 4000
        }
        
        try:
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS with {model}!")
                return model, result['choices'][0]['message']['content']
            else:
                print(f"❌ ERROR with {model}: {response.status_code}")
                if response.status_code == 404:
                    print(f"Model {model} not available, trying next...")
                    continue
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ EXCEPTION with {model}: {e}")
    
    return None, None

if __name__ == "__main__":
    model, analysis = test_gpt5_thinking()
    if model and analysis:
        print(f"\n🎉 Best working model: {model}")
        print("\n" + "="*80)
        print("GPT-5-THINKING ULTIMATIVE VALIDIERUNG:")
        print("="*80)
        print(analysis)
        print("="*80)
    else:
        print("\n❌ No working models found")




