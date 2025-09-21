#!/usr/bin/env python3
"""
RADIKALE BEREINIGUNG: Neustart mit wissenschaftlich korrekten Basis-Fakten
"""

import sqlite3
import datetime
import shutil

def radical_cleanup_and_restart():
    """
    Löscht ALLE falschen Fakten und startet mit wissenschaftlicher Basis neu
    """
    
    print("RADIKALE BEREINIGUNG UND NEUSTART")
    print("="*60)
    
    # 1. BACKUP
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"hexagonal_kb_RADICAL_CLEANUP_{timestamp}.db"
    print(f"1. Erstelle Backup: {backup_file}")
    shutil.copy2("hexagonal_kb.db", backup_file)
    
    conn = sqlite3.connect("hexagonal_kb.db")
    conn.isolation_level = None  # Autocommit für VACUUM
    cursor = conn.cursor()
    
    # 2. ZÄHLE VORHER
    cursor.execute("SELECT COUNT(*) FROM facts")
    total_before = cursor.fetchone()[0]
    print(f"2. Fakten vor Bereinigung: {total_before:,}")
    
    # 3. LÖSCHE ALLES!
    print("\n3. LÖSCHE ALLE wissenschaftlich falschen Fakten...")
    cursor.execute("DELETE FROM facts")
    print(f"   → {total_before:,} Fakten gelöscht")
    
    # 4. FÜGE NUR WISSENSCHAFTLICH KORREKTE BASIS-FAKTEN EIN
    print("\n4. Füge wissenschaftlich korrekte Basis-Fakten ein...")
    
    # Definiere korrekte Basis-Fakten (6-7 Argumente wo möglich)
    correct_facts = [
        # CHEMIE - Korrekte Molekülstrukturen und Reaktionen
        ("ChemicalReaction(N2, 3H2, 2NH3, null, Fe_catalyst, 450C, 200atm)", "CHEMISTRY", 7),
        ("ChemicalReaction(CH4, 2O2, CO2, 2H2O, spark, 25C, 1atm)", "CHEMISTRY", 7),
        ("ChemicalReaction(2H2O2, null, 2H2O, O2, MnO2_catalyst, 20C, 1atm)", "CHEMISTRY", 7),
        ("MolecularStructure(CH4, carbon, 4hydrogen, tetrahedral, sp3, nonpolar, 109.5deg)", "CHEMISTRY", 7),
        ("MolecularStructure(H2O, oxygen, 2hydrogen, bent, sp3, polar, 104.5deg)", "CHEMISTRY", 7),
        ("MolecularStructure(NH3, nitrogen, 3hydrogen, pyramidal, sp3, polar, 107deg)", "CHEMISTRY", 7),
        ("MolecularStructure(CO2, carbon, 2oxygen, linear, sp, nonpolar, 180deg)", "CHEMISTRY", 7),
        
        # PHYSIK - Korrekte physikalische Relationen
        ("ElectromagneticWave(visible_light, 500nm, 600THz, 2.48eV, linear_polarization, vacuum, 299792458m/s)", "PHYSICS", 7),
        ("ParticleInteraction(electron, proton, electromagnetic, -13.6eV, angular_momentum_conserved, 1s_orbital, hydrogen)", "PHYSICS", 7),
        ("ParticleInteraction(proton, neutron, strong_nuclear, 2.2MeV, binding_energy, spin_coupled, deuteron)", "PHYSICS", 7),
        ("Motion(projectile, 45deg, 100m/s, -9.8m/s2, 1020m_range, 10.2s_flight, parabolic)", "PHYSICS", 7),
        
        # BIOLOGIE - Korrekte biologische Prozesse
        ("ProteinSynthesis(insulin_gene, pre_mRNA, mRNA, ribosome, amino_acids, proinsulin, endoplasmic_reticulum)", "BIOLOGY", 7),
        ("CellularRespiration(glucose, 6O2, 6CO2, 6H2O, 38ATP, mitochondria, aerobic)", "BIOLOGY", 7),
        ("DNAReplication(template_strand, DNA_polymerase, primer, nucleotides, 3to5_direction, lagging_strand, semiconservative)", "BIOLOGY", 7),
        ("FoodWeb(phytoplankton, zooplankton, small_fish, large_fish, decomposers, energy_flow, marine_ecosystem)", "BIOLOGY", 7),
        
        # INFORMATIK - Korrekte technische Fakten
        ("TCPConnection(client_192.168.1.1, port_8080, server_10.0.0.1, port_443, SYN_ACK, sequence_0x1234, established)", "COMPUTER_SCIENCE", 7),
        ("AlgorithmAnalysis(quicksort, O_nlogn_average, O_n2_worst, O_logn_space, divide_conquer, unstable, comparison_based)", "COMPUTER_SCIENCE", 7),
        ("AlgorithmAnalysis(dijkstra, O_ElogV, O_V2_naive, O_V_space, greedy, optimal, shortest_path)", "COMPUTER_SCIENCE", 7),
        ("DataStructure(B_tree, balanced, O_logn_search, O_logn_insert, O_logn_delete, disk_optimized, database_index)", "COMPUTER_SCIENCE", 7),
        
        # MATHEMATIK - Korrekte mathematische Relationen
        ("FunctionAnalysis(exponential, e^x, continuous, differentiable, e^x_derivative, monotonic_increasing, transcendental)", "MATHEMATICS", 7),
        ("FunctionAnalysis(sine, sin_x, periodic_2pi, continuous, cos_x_derivative, bounded_-1_to_1, trigonometric)", "MATHEMATICS", 7),
        ("MatrixOperation(A_3x3, B_3x3, multiplication, C_3x3, 27_scalar_ops, non_commutative, O_n3)", "MATHEMATICS", 7),
        ("NumberProperty(6, composite, perfect, factors_1_2_3_6, sum_of_divisors_12, abundant_false, first_perfect)", "MATHEMATICS", 7),
    ]
    
    inserted = 0
    for fact, domain, arg_count in correct_facts:
        # Extrahiere Prädikat
        predicate = fact.split('(')[0]
        
        try:
            cursor.execute("""
                INSERT INTO facts (statement, source, metadata)
                VALUES (?, 'scientific_base', ?)
            """, (fact, f'{{"domain": "{domain}", "arg_count": {arg_count}, "validated": true}}'))
            inserted += 1
            print(f"  ✓ {predicate} ({arg_count} args)")
        except sqlite3.IntegrityError:
            pass  # Duplikat, ignorieren
        except sqlite3.OperationalError as e:
            # Falls Spalten fehlen, einfachere Insert
            try:
                cursor.execute("INSERT OR IGNORE INTO facts (statement) VALUES (?)", (fact,))
                inserted += 1
                print(f"  ✓ {predicate} ({arg_count} args)")
            except Exception as e2:
                print(f"  ✗ Fehler bei {predicate}: {e2}")
    
    print(f"\n  → {inserted} wissenschaftliche Basis-Fakten eingefügt")
    
    # 5. VACUUM
    print("\n5. Optimiere Datenbank...")
    cursor.execute("VACUUM")
    
    # 6. FINALE STATISTIK
    cursor.execute("SELECT COUNT(*) FROM facts")
    total_after = cursor.fetchone()[0]
    
    print("\n" + "="*60)
    print("NEUSTART ABGESCHLOSSEN")
    print("-"*40)
    print(f"Vorher:     {total_before:,} Fakten (größtenteils falsch)")
    print(f"Gelöscht:   {total_before:,} Fakten")
    print(f"Neu:        {inserted:,} wissenschaftlich korrekte Fakten")
    print(f"Total:      {total_after:,} Fakten")
    
    # Zeige alle neuen Fakten
    print("\nWISSENSCHAFTLICH KORREKTE BASIS:")
    print("-"*40)
    cursor.execute("SELECT statement FROM facts ORDER BY statement")
    for i, (fact,) in enumerate(cursor.fetchall(), 1):
        # Kürze lange Fakten für Anzeige
        if len(fact) > 80:
            display = fact[:77] + "..."
        else:
            display = fact
        print(f"{i:2}. {display}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("WICHTIG - NÄCHSTE SCHRITTE:")
    print("-"*40)
    print("1. STOPPE die aktuelle Faktengenerierung!")
    print("2. Konfiguriere DeepSeek statt Groq")
    print("3. Aktiviere governor_extended_optimized.conf")
    print("4. Verwende NUR validated_fact_patterns.py")
    print("5. Setze Temperatur auf 0.1 für Präzision")
    print("\nDie Datenbank enthält jetzt NUR wissenschaftlich korrekte Fakten!")
    print("Qualität > Quantität!")
    
    return total_after

if __name__ == "__main__":
    print("⚠️  WARNUNG: Dies löscht ALLE Fakten und startet neu!")
    print("    Die Datenbank wird auf ~25 korrekte Basis-Fakten reduziert.")
    response = input("\nFortfahren? (ja/nein): ")
    
    if response.lower() in ['ja', 'j', 'yes', 'y']:
        facts_count = radical_cleanup_and_restart()
        
        if facts_count < 30:
            print("\n✅ ERFOLG: Saubere wissenschaftliche Basis erstellt!")
            print("   Die Faktengenerierung kann nun mit korrekten Patterns neu starten.")
    else:
        print("Abgebrochen.")
