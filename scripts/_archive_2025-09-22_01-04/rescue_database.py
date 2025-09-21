#!/usr/bin/env python3
"""
HAK-GAL Datenbank-Rettungsplan
================================
Extrahiert und bewahrt nur die sicheren, verifizierten Fakten
"""

import sqlite3
import re
from datetime import datetime
import json
from collections import defaultdict

class DatabaseRescue:
    def __init__(self, db_path="hexagonal_kb.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.safe_facts = []
        self.fixable_facts = []
        self.report = []
        
    def identify_safe_facts(self):
        """Identifiziert definitiv sichere Fakten"""
        
        print("="*80)
        print("PHASE 1: IDENTIFIKATION SICHERER FAKTEN")
        print("="*80)
        
        # 1. Human-verifizierte Fakten
        print("\n1. Sammle human-verifizierte Fakten...")
        self.cursor.execute("""
            SELECT rowid, statement, source 
            FROM facts 
            WHERE context LIKE '%human_verified%'
        """)
        human_verified = self.cursor.fetchall()
        
        for row in human_verified:
            self.safe_facts.append({
                'id': row[0],
                'statement': row[1],
                'category': 'human_verified',
                'confidence': 1.0
            })
        print(f"   ✓ {len(human_verified)} human-verifizierte Fakten gefunden")
        
        # 2. Korrekte chemische Formeln
        print("\n2. Sammle korrekte chemische Formeln...")
        correct_chemistry = [
            "ConsistsOf(H2O, hydrogen, oxygen).",
            "ConsistsOf(NH3, nitrogen, hydrogen).",
            "ConsistsOf(CO2, carbon, oxygen).",
            "ConsistsOf(CH4, carbon, hydrogen).",
            "ConsistsOf(NaCl, sodium, chlorine).",
            "ConsistsOf(O2, oxygen).",
            "ConsistsOf(N2, nitrogen).",
            "ConsistsOf(HCl, hydrogen, chlorine).",
        ]
        
        found_chemistry = 0
        for formula in correct_chemistry:
            self.cursor.execute("SELECT rowid FROM facts WHERE statement = ?", (formula,))
            result = self.cursor.fetchone()
            if result:
                self.safe_facts.append({
                    'id': result[0],
                    'statement': formula,
                    'category': 'verified_chemistry',
                    'confidence': 1.0
                })
                found_chemistry += 1
        print(f"   ✓ {found_chemistry} korrekte chemische Formeln gefunden")
        
        # 3. Verifizierte biologische Fakten
        print("\n3. Sammle verifizierte biologische Fakten...")
        bio_patterns = [
            ("DNA", ["nucleotide", "phosphate", "sugar"]),
            ("protein", ["amino_acid"]),
            ("cell", ["membrane", "cytoplasm"]),
            ("ribosome", ["RNA", "protein"]),
        ]
        
        found_bio = 0
        for entity, components in bio_patterns:
            for component in components:
                self.cursor.execute("""
                    SELECT rowid, statement 
                    FROM facts 
                    WHERE (statement LIKE ? OR statement LIKE ?)
                    AND (statement LIKE ? OR statement LIKE ?)
                    AND statement NOT LIKE '%virus%organ%'
                    AND statement NOT LIKE '%bacteria%nucleus%'
                """, (f'%{entity}%', f'%{entity.upper()}%', 
                     f'%{component}%', f'%{component.upper()}%'))
                
                results = self.cursor.fetchall()
                for row_id, stmt in results:
                    if self._is_biologically_correct(stmt):
                        self.safe_facts.append({
                            'id': row_id,
                            'statement': stmt,
                            'category': 'verified_biology',
                            'confidence': 0.9
                        })
                        found_bio += 1
        print(f"   ✓ {found_bio} verifizierte biologische Fakten gefunden")
        
        # 4. Hochwertige Cluster-Fakten
        print("\n4. Sammle hochwertige Cluster-Fakten...")
        quality_subjects = [
            'MachineLearning', 'NeuralNetworks', 'DeepLearning',
            'QuantumMechanics', 'Mathematics', 'Algorithm'
        ]
        
        found_cluster = 0
        for subject in quality_subjects:
            self.cursor.execute("""
                SELECT rowid, statement 
                FROM facts 
                WHERE subject = ? 
                AND predicate IN ('HasPart', 'IsTypeOf', 'Uses', 'Requires')
                AND confidence >= 1.0
            """, (subject,))
            
            results = self.cursor.fetchall()
            for row_id, stmt in results:
                if self._is_plausible(stmt):
                    self.safe_facts.append({
                        'id': row_id,
                        'statement': stmt,
                        'category': f'cluster_{subject}',
                        'confidence': 0.8
                    })
                    found_cluster += 1
        print(f"   ✓ {found_cluster} hochwertige Cluster-Fakten gefunden")
        
        return self.safe_facts
    
    def identify_fixable_facts(self):
        """Identifiziert korrigierbare Fakten"""
        
        print("\n" + "="*80)
        print("PHASE 2: IDENTIFIKATION KORRIGIERBARER FAKTEN")
        print("="*80)
        
        # Falsche chemische Aussagen die korrigiert werden können
        fixable_patterns = [
            # (Suchmuster, Fehlertyp, Korrektur)
            ("%NH3%oxygen%", "NH3_oxygen", "ConsistsOf(NH3, nitrogen, hydrogen)."),
            ("%H2O%carbon%", "H2O_carbon", "ConsistsOf(H2O, hydrogen, oxygen)."),
            ("%CH4%oxygen%ConsistsOf%", "CH4_oxygen", "ConsistsOf(CH4, carbon, hydrogen)."),
            ("%CO2%hydrogen%ConsistsOf%", "CO2_hydrogen", "ConsistsOf(CO2, carbon, oxygen)."),
            ("%virus%organ%", "virus_organ", None),  # Löschen
            ("%bacteria%nucleus%", "bacteria_nucleus", None),  # Löschen
        ]
        
        for pattern, error_type, correction in fixable_patterns:
            self.cursor.execute(f"SELECT rowid, statement FROM facts WHERE statement LIKE ?", (pattern,))
            results = self.cursor.fetchall()
            
            for row_id, stmt in results:
                self.fixable_facts.append({
                    'id': row_id,
                    'statement': stmt,
                    'error_type': error_type,
                    'correction': correction,
                    'action': 'fix' if correction else 'delete'
                })
        
        print(f"   ✓ {len(self.fixable_facts)} korrigierbare Fakten identifiziert")
        print(f"      - Zu korrigieren: {sum(1 for f in self.fixable_facts if f['action'] == 'fix')}")
        print(f"      - Zu löschen: {sum(1 for f in self.fixable_facts if f['action'] == 'delete')}")
        
        return self.fixable_facts
    
    def _is_biologically_correct(self, statement):
        """Prüft biologische Korrektheit"""
        stmt_lower = statement.lower()
        
        # Bekannte Fehler
        if 'virus' in stmt_lower and 'organ' in stmt_lower:
            return False
        if 'bacteria' in stmt_lower and 'nucleus' in stmt_lower:
            return False
        
        # Plausibilitäts-Checks
        if 'dna' in stmt_lower:
            return any(term in stmt_lower for term in ['nucleotide', 'base', 'sugar', 'phosphate'])
        if 'protein' in stmt_lower:
            return 'amino' in stmt_lower or 'acid' in stmt_lower
        
        return True
    
    def _is_plausible(self, statement):
        """Prüft allgemeine Plausibilität"""
        # Einfache Längen- und Struktur-Checks
        if len(statement) < 10 or len(statement) > 200:
            return False
        if statement.count('(') != 1 or statement.count(')') != 1:
            return False
        
        # Keine offensichtlichen Fehler
        errors = ['nh3, oxygen', 'h2o, carbon', 'virus, organ']
        stmt_lower = statement.lower()
        return not any(error in stmt_lower for error in errors)
    
    def generate_rescue_report(self):
        """Generiert Rettungsbericht"""
        
        print("\n" + "="*80)
        print("RETTUNGSBERICHT")
        print("="*80)
        
        # Statistik
        total_facts = self.cursor.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        
        categories = defaultdict(int)
        for fact in self.safe_facts:
            categories[fact['category']] += 1
        
        print(f"\nDATENBANK-STATUS:")
        print(f"  Total Fakten: {total_facts:,}")
        print(f"  Sichere Fakten: {len(self.safe_facts):,} ({len(self.safe_facts)/total_facts*100:.1f}%)")
        print(f"  Korrigierbare Fakten: {len(self.fixable_facts):,}")
        
        print(f"\nSICHERE FAKTEN NACH KATEGORIE:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        
        print(f"\nEMPFOHLENE AKTIONEN:")
        print(f"  1. Sichere {len(self.safe_facts)} Fakten in neue Tabelle 'facts_verified'")
        print(f"  2. Korrigiere {sum(1 for f in self.fixable_facts if f['action'] == 'fix')} fehlerhafte Fakten")
        print(f"  3. Lösche {sum(1 for f in self.fixable_facts if f['action'] == 'delete')} unrettbare Fakten")
        print(f"  4. Markiere verbleibende {total_facts - len(self.safe_facts) - len(self.fixable_facts):,} als 'needs_review'")
        
        # Speichere Bericht
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_facts': total_facts,
            'safe_facts': len(self.safe_facts),
            'fixable_facts': len(self.fixable_facts),
            'categories': dict(categories),
            'safe_facts_sample': self.safe_facts[:20],
            'fixable_facts_sample': self.fixable_facts[:20]
        }
        
        with open('rescue_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nBericht gespeichert in: rescue_report.json")
        
        return report_data
    
    def create_verified_table(self):
        """Erstellt Tabelle mit verifizierten Fakten"""
        
        print("\n" + "="*80)
        print("ERSTELLE VERIFIZIERTE FAKTEN-TABELLE")
        print("="*80)
        
        # Erstelle neue Tabelle
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts_verified (
                id INTEGER PRIMARY KEY,
                statement TEXT UNIQUE,
                category TEXT,
                confidence REAL,
                original_id INTEGER,
                verified_date TEXT
            )
        """)
        
        # Füge sichere Fakten ein
        inserted = 0
        for fact in self.safe_facts:
            try:
                self.cursor.execute("""
                    INSERT INTO facts_verified (statement, category, confidence, original_id, verified_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (fact['statement'], fact['category'], fact['confidence'], 
                      fact['id'], datetime.now().isoformat()))
                inserted += 1
            except sqlite3.IntegrityError:
                pass  # Duplikat, überspringen
        
        self.conn.commit()
        print(f"   ✓ {inserted} verifizierte Fakten in 'facts_verified' gespeichert")
        
        return inserted

def main():
    print("HAK-GAL DATENBANK-RETTUNG")
    print("="*80)
    print("Starte Rettungsoperation...")
    
    rescue = DatabaseRescue()
    
    # Phase 1: Sichere Fakten identifizieren
    rescue.identify_safe_facts()
    
    # Phase 2: Korrigierbare Fakten identifizieren
    rescue.identify_fixable_facts()
    
    # Phase 3: Bericht generieren
    report = rescue.generate_rescue_report()
    
    # Phase 4: Verifizierte Tabelle erstellen
    rescue.create_verified_table()
    
    print("\n" + "="*80)
    print("RETTUNGSOPERATION ABGESCHLOSSEN")
    print(f"✓ {report['safe_facts']} sichere Fakten identifiziert und gesichert")
    print(f"✓ {report['fixable_facts']} Fakten können korrigiert werden")
    print("✓ Neue Tabelle 'facts_verified' erstellt")
    print("="*80)

if __name__ == "__main__":
    main()
