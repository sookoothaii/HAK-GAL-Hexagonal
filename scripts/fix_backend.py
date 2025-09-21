#!/usr/bin/env python3
"""
BACKEND FIX SCRIPT
Behebt die kritischen Probleme im HAK-GAL Backend
"""

import os
import sqlite3
import shutil
from datetime import datetime

def fix_backend_issues():
    """
    Behebt alle Backend-Probleme systematisch
    """
    
    print("HAK-GAL BACKEND FIX")
    print("="*60)
    
    # 1. HRM MODEL RESET
    print("\n1. HRM Model Reset...")
    hrm_path = "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\models\\hrm_model.pth"
    if os.path.exists(hrm_path):
        backup = f"{hrm_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.move(hrm_path, backup)
        print(f"   ✓ Altes Model gesichert: {backup}")
        print("   ✓ Neues Model wird beim Start automatisch erstellt")
    else:
        print("   ℹ Kein altes Model gefunden")
    
    # 2. DATENBANK BEREINIGUNG
    print("\n2. Datenbank-Bereinigung...")
    
    # Backup
    db_path = "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"   ✓ Backup erstellt: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    conn.isolation_level = None
    cursor = conn.cursor()
    
    # Zähle vorher
    cursor.execute("SELECT COUNT(*) FROM facts")
    before = cursor.fetchone()[0]
    print(f"   ℹ Fakten vorher: {before:,}")
    
    # RADIKALE BEREINIGUNG - Nur wissenschaftlich korrekte behalten
    print("   🗑️ Lösche wissenschaftlich falsche Fakten...")
    
    # Lösche ALLE außer den verifizierten
    cursor.execute("DELETE FROM facts")
    
    # Füge nur verifizierte wissenschaftliche Basis-Fakten ein
    scientific_facts = [
        # CHEMIE - 7 Argumente
        "ChemicalReaction(N2, 3H2, 2NH3, null, Fe_catalyst, 450C, 200atm)",
        "ChemicalReaction(CH4, 2O2, CO2, 2H2O, spark, 25C, 1atm)",
        "MolecularStructure(H2O, oxygen, 2hydrogen, bent, sp3, polar, 104.5deg)",
        "MolecularStructure(CH4, carbon, 4hydrogen, tetrahedral, sp3, nonpolar, 109.5deg)",
        "MolecularStructure(NH3, nitrogen, 3hydrogen, pyramidal, sp3, polar, 107deg)",
        "MolecularStructure(CO2, carbon, 2oxygen, linear, sp, nonpolar, 180deg)",
        
        # PHYSIK - 7 Argumente
        "ElectromagneticWave(visible_light, 500nm, 600THz, 2.48eV, linear, vacuum, 299792458m/s)",
        "ParticleInteraction(electron, proton, electromagnetic, -13.6eV, conserved, 1s_orbital, hydrogen)",
        "Motion(projectile, 45deg, 100m/s, -9.8m/s2, 1020m, 10.2s, parabolic)",
        
        # BIOLOGIE - 7 Argumente  
        "ProteinSynthesis(insulin_gene, mRNA, ribosome, tRNA, amino_acids, insulin, cytoplasm)",
        "CellularRespiration(glucose, 6O2, 6CO2, 6H2O, 38ATP, mitochondria, aerobic)",
        "DNAReplication(template, DNA_polymerase, primer, nucleotides, 3to5, lagging, semiconservative)",
        
        # INFORMATIK - 7 Argumente
        "AlgorithmAnalysis(quicksort, O_nlogn, O_n2, O_logn, divide_conquer, unstable, comparison)",
        "TCPConnection(192.168.1.1, 8080, 10.0.0.1, 443, SYN_ACK, seq_1234, established)",
        "DataStructure(B_tree, balanced, O_logn, O_logn, O_logn, disk_optimized, database)",
        
        # MATHEMATIK - 7 Argumente
        "FunctionAnalysis(exponential, e^x, continuous, differentiable, e^x, monotonic, transcendental)",
        "MatrixOperation(A_3x3, B_3x3, multiply, C_3x3, 27_ops, non_commutative, O_n3)",
        "NumberProperty(6, composite, perfect, factors_1_2_3_6, sum_12, false, first_perfect)"
    ]
    
    inserted = 0
    for fact in scientific_facts:
        try:
            cursor.execute("INSERT INTO facts (statement) VALUES (?)", (fact,))
            inserted += 1
        except:
            pass
    
    print(f"   ✓ {inserted} wissenschaftliche Basis-Fakten eingefügt")
    
    # Vacuum
    cursor.execute("VACUUM")
    
    # Zähle nachher
    cursor.execute("SELECT COUNT(*) FROM facts")
    after = cursor.fetchone()[0]
    
    print(f"   ✓ Fakten nachher: {after}")
    print(f"   ✓ Reduzierung: {((before-after)/before*100):.1f}%")
    
    conn.close()
    
    # 3. GOVERNOR KONFIGURATION
    print("\n3. Governor-Konfiguration...")
    
    config = """# OPTIMIERTE GOVERNOR CONFIGURATION
[engine]
provider = deepseek  # Wechsel von groq zu deepseek
temperature = 0.1  # Sehr niedrig für Präzision
min_arguments = 6
max_arguments = 7

[validation]  
enable_strict = true
min_confidence = 0.8
reject_vague = true
reject_person_physics = true

[generation]
use_validated_patterns = true
facts_per_batch = 5  # Weniger aber besser

[domains]
enabled = ["CHEMISTRY", "PHYSICS", "BIOLOGY", "COMPUTER_SCIENCE", "MATHEMATICS"]
disabled = ["GENERAL", "PHILOSOPHY", "HISTORY"]
"""
    
    with open("D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\governor.conf", "w") as f:
        f.write(config)
    
    print("   ✓ Governor auf DeepSeek + strikte Validierung umgestellt")
    
    # 4. ENV VARIABLES
    print("\n4. Umgebungsvariablen prüfen...")
    
    env_file = "D:\\MCP Mods\\hak_gal_user\\.env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            content = f.read()
        
        if "DEEPSEEK_API_KEY" not in content:
            print("   ⚠️ DEEPSEEK_API_KEY fehlt in .env")
            print("   → Bitte hinzufügen: DEEPSEEK_API_KEY=your_key_here")
        else:
            print("   ✓ DEEPSEEK_API_KEY gefunden")
            
        if "SENTRY_DSN" in content and "your-dsn-here" in content:
            print("   ⚠️ SENTRY_DSN ist Platzhalter")
            print("   → Entfernen oder echten DSN eintragen")
    
    # 5. ZUSAMMENFASSUNG
    print("\n" + "="*60)
    print("✅ BACKEND FIXES ANGEWENDET:")
    print("-"*40)
    print("1. HRM Model zurückgesetzt → wird neu trainiert")
    print(f"2. Datenbank bereinigt → {after} wissenschaftliche Fakten")
    print("3. Governor auf DeepSeek + strikte Validierung")
    print("4. Konfiguration optimiert")
    
    print("\n⚠️ NÄCHSTE SCHRITTE:")
    print("-"*40)
    print("1. Backend neu starten:")
    print("   python hexagonal_api_enhanced_clean.py")
    print("\n2. DeepSeek API Key setzen (falls nicht vorhanden):")
    print("   $env:DEEPSEEK_API_KEY='your_key'")
    print("\n3. LLM Governor aktivieren:")
    print("   curl -X POST http://localhost:5002/api/llm-governor/enable")
    
    return after

if __name__ == "__main__":
    print("⚠️ WARNUNG: Dies bereinigt die Datenbank radikal!")
    print("   Nur ~20 wissenschaftlich korrekte Fakten bleiben.")
    
    response = input("\nFortfahren? (ja/nein): ")
    
    if response.lower() in ['ja', 'j', 'yes', 'y']:
        facts = fix_backend_issues()
        
        if facts < 50:
            print("\n✅ ERFOLG! Backend ist bereit für wissenschaftliche Faktengenerierung")
            print("   Starten Sie das Backend neu für die Änderungen.")
    else:
        print("Abgebrochen.")
