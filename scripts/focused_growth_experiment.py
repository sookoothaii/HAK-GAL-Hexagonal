import requests
import json
import time
import re

# --- KONFIGURATION DES EXPERIMENTS ---

# 1. API-Endpunkte des HAK/GAL-Servers
API_BASE_URL = "http://localhost:5002/api"
LLM_EXPLAIN_URL = f"{API_BASE_URL}/llm/get-explanation"
FACTS_URL = f"{API_BASE_URL}/facts"
SEARCH_URL = f"{API_BASE_URL}/search"

# 2. Authentifizierung (wird für die meisten Endpunkte nicht benötigt, aber für zukünftige Erweiterungen beibehalten)
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

# 3. Experiment-Parameter
TOPIC = "Die Römische Republik"
# WICHTIG: Fakten müssen dem Server-Format Predicate(Entity1,Entity2). entsprechen
SEED_FACTS = [
    "WurdeGegruendetIn(RoemischeRepublik, 509_v_Chr).",
    "EndeteMit(RoemischeRepublik, AufstiegDesAugustus).",
    "HatteSozialeKlassen(RoemischeRepublik, PatrizierUndPlebejer)."
]
CYCLES = 5
BEAM_WIDTH = 3 # Wird nicht mehr für die Generierung, aber als Indikator für die Komplexität des Themas beibehalten


# --- HILFSFUNKTIONEN ---

def call_hakgal_api(endpoint_url: str, method: str = 'POST', payload: dict = None) -> dict:
    """
    Eine generische Funktion, um die HAK/GAL API Endpunkte aufzurufen.
    """
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    print(f"    [API Call] Ziel: {endpoint_url}, Methode: {method}")

    try:
        response = requests.request(method, endpoint_url, headers=headers, json=payload, timeout=120) # Timeout erhöht für LLM
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"    [API Error] Fehler bei der Kommunikation mit dem HAK/GAL Server: {e}")
        return {"error": str(e)}


# --- HAUPT-EXPERIMENT ---

def run_experiment():
    """
    Führt den fokussierten Wissens-Wachstums-Zyklus durch.
    """
    print("--- Starte HAK/GAL Fokussiertes Wachstums-Experiment (V3 - Direkt-LLM) ---")
    print(f"Thema: {TOPIC}")
    print(f"Zyklen: {CYCLES}")
    print("---------------------------------------------------------------------\
")

    # Initialisiere die Wissensbasis mit den Samen-Fakten
    print("[Phase 0: Initialisierung]")
    for fact in SEED_FACTS:
        print(f"  -> Füge Samen-Fakt hinzu: \"{fact}\"")
        add_payload = {"statement": fact, "source": "seed_experiment"}
        call_hakgal_api(FACTS_URL, payload=add_payload)
    
    time.sleep(1)
    
    frontier = list(SEED_FACTS)
    known_facts_set = set(SEED_FACTS)
    stats = {"added": 0, "rejected_redundant": 0, "rejected_error": 0}

    # --- Der Haupt-Zyklus ---
    for i in range(CYCLES):
        print(f"\n--- [Zyklus {i+1}/{CYCLES}] ---")
        if not frontier:
            print("  [Warnung] Wissens-Frontier ist leer. Experiment wird beendet.")
            break
            
        base_fact = frontier.pop(0)
        print(f"  [Thesis Engine] Expandiere basierend auf dem Thema '{TOPIC}' mit Kontext: \"{base_fact}\"")

        # 1. THESIS: Generiere neue Fakten direkt über den LLM-Endpunkt des Servers
        llm_payload = {"topic": TOPIC, "context_facts": [base_fact]}
        response = call_hakgal_api(LLM_EXPLAIN_URL, payload=llm_payload)

        if not response or "suggested_facts" not in response:
            print(f"  [Thesis Error] Keine Faktenvorschläge vom LLM-Endpunkt erhalten: {response}")
            stats["rejected_error"] += BEAM_WIDTH # Schätzung
            continue

        candidate_facts = response["suggested_facts"]
        print(f"  -> {len(candidate_facts)} Kandidaten vom Server erhalten.")

        # 2. AETHELRED & AKQUISITION: Prüfe und füge hinzu
        for candidate in candidate_facts:
            # Validiere das Format des Kandidaten
            if not isinstance(candidate, str) or not (candidate.startswith("Predicate(") or re.match(r"^[A-Za-z_][A-Za-z0-9_]*\([^,)]+,\s*[^\)]+\)\.$", candidate)):
                print(f"  [Aethelred] Verwerfe ungültigen Kandidaten (Format): {candidate}")
                stats["rejected_error"] += 1
                continue

            if candidate in known_facts_set:
                print(f"  [Aethelred] Verwerfe Duplikat: {candidate}")
                stats["rejected_redundant"] += 1
                continue

            print(f"    [Akquisition] ACCEPTED: Füge neuen, validen Fakt hinzu: {candidate}")
            add_payload = {"statement": candidate, "source": f"cycle_{i+1}_llm"}
            add_result = call_hakgal_api(FACTS_URL, payload=add_payload)
            
            if add_result and add_result.get("success"):
                stats["added"] += 1
                frontier.append(candidate)
                known_facts_set.add(candidate)
            else:
                # Fehler kann auch "fact already exists" sein, was wir als Redundanz zählen
                message = add_result.get('message', '')
                print(f"      [Akquisition Info] Fakt konnte nicht hinzugefügt werden: {message}")
                if "exists" in message.lower() or "existiert bereits" in message.lower():
                    stats["rejected_redundant"] += 1
                else:
                    stats["rejected_error"] += 1
        
        time.sleep(2)

    # --- ABSCHLUSSBERICHT ---
    print("\n\n--- [Experiment Abgeschlossen: Abschlussbericht] ---")
    print(f"Thema: {TOPIC}")
    print("\n**Metriken:**")
    print(f"  - Neue Fakten hinzugefügt: {stats['added']}")
    print(f"  - Fakten wegen Redundanz/Duplikat verworfen: {stats['rejected_redundant']}")
    print(f"  - Fakten wegen Fehlern/Formatproblemen verworfen: {stats['rejected_error']}")
    
    print("\n**Neu erworbenes Wissen (Auszug):**")
    final_facts = sorted(list(known_facts_set - set(SEED_FACTS)))
    if final_facts:
        for i, fact in enumerate(final_facts[:20]): # Zeige max. 20 neue Fakten
            print(f"  {i+1}. {fact}")
    else:
        print("  -> Keine neuen Fakten wurden der Wissensdatenbank hinzugefügt.")

    print("\n----------------------------------------------------")
    print("ANALYSE: Überprüfen Sie die Qualität und das Format der generierten Fakten.")
    print("VERBESSERUNG: Die Qualität hängt nun direkt von der Leistung des /api/llm/get-explanation Endpunkts ab.")


if __name__ == "__main__":
    run_experiment()