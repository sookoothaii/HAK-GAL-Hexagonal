#!/usr/bin/env python3
"""
STRIKTER WISSENSCHAFTLICHER FAKTEN-VALIDATOR
Mit JSON-Schema und fachspezifischen Checks pro Domain
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from jsonschema import validate, ValidationError

# JSON-Schema für Validierungs-Response
VALIDATION_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["is_valid", "confidence", "issues", "domain_check", "scientific_accuracy"],
    "properties": {
        "is_valid": {"type": "boolean"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "issues": {
            "type": "array",
            "items": {"type": "string"}
        },
        "domain_check": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "passed": {"type": "boolean"},
                "details": {"type": "string"}
            }
        },
        "scientific_accuracy": {
            "type": "object",
            "properties": {
                "conservation_laws": {"type": "boolean"},
                "units_correct": {"type": "boolean"},
                "values_plausible": {"type": "boolean"},
                "references_valid": {"type": "boolean"}
            }
        },
        "corrected_fact": {"type": ["string", "null"]}
    }
}

class ScientificFactValidator:
    """
    Strikter Validator mit Domain-spezifischen wissenschaftlichen Checks
    """
    
    def __init__(self):
        self.domain_validators = {
            "CHEMISTRY": self._validate_chemistry,
            "PHYSICS": self._validate_physics,
            "BIOLOGY": self._validate_biology,
            "COMPUTER_SCIENCE": self._validate_cs,
            "MATHEMATICS": self._validate_math
        }
        
        # Wissenschaftliche Konstanten für Validierung
        self.constants = {
            "speed_of_light": 299792458,  # m/s
            "avogadro": 6.022e23,
            "planck": 6.626e-34,  # J⋅s
            "electron_charge": 1.602e-19,  # C
        }
    
    def validate_fact(self, fact: str, domain: str) -> Dict:
        """
        Hauptvalidierungsfunktion
        """
        result = {
            "is_valid": True,
            "confidence": 1.0,
            "issues": [],
            "domain_check": {
                "domain": domain,
                "passed": False,
                "details": ""
            },
            "scientific_accuracy": {
                "conservation_laws": True,
                "units_correct": True,
                "values_plausible": True,
                "references_valid": True
            },
            "corrected_fact": None
        }
        
        # 1. STRUKTUR-CHECK
        structure_check = self._check_structure(fact)
        if not structure_check["valid"]:
            result["is_valid"] = False
            result["confidence"] = 0.0
            result["issues"].extend(structure_check["issues"])
            return result
        
        # 2. ARGUMENT-COUNT CHECK (6-7 für Komplexität)
        arg_count = fact.count(',') + 1
        if arg_count < 6:
            result["issues"].append(f"Nur {arg_count} Argumente (min. 6 erforderlich)")
            result["confidence"] *= 0.7
        elif arg_count > 7:
            result["issues"].append(f"{arg_count} Argumente (max. 7 erlaubt)")
            result["confidence"] *= 0.8
        
        # 3. DOMAIN-SPEZIFISCHER CHECK
        if domain in self.domain_validators:
            domain_result = self.domain_validators[domain](fact)
            result["domain_check"] = domain_result
            
            if not domain_result["passed"]:
                result["is_valid"] = False
                result["confidence"] *= 0.3
                result["issues"].append(f"Domain-Check fehlgeschlagen: {domain_result['details']}")
        
        # 4. WISSENSCHAFTLICHE PLAUSIBILITÄT
        sci_check = self._check_scientific_plausibility(fact, domain)
        result["scientific_accuracy"].update(sci_check)
        
        if not all(sci_check.values()):
            result["confidence"] *= 0.5
            for key, value in sci_check.items():
                if not value:
                    result["issues"].append(f"Wissenschaftlicher Fehler: {key}")
        
        # 5. FINALE BEWERTUNG
        if len(result["issues"]) > 2:
            result["is_valid"] = False
        
        if result["confidence"] < 0.6:
            result["is_valid"] = False
        
        return result
    
    def _check_structure(self, fact: str) -> Dict:
        """
        Prüft die syntaktische Struktur des Fakts
        """
        issues = []
        
        # Muss Prädikat(args) Format haben
        if not re.match(r'^[A-Z][a-zA-Z]+\([^)]+\)$', fact):
            issues.append("Ungültiges Format (erwartet: Predicate(args))")
        
        # Keine leeren Argumente
        if ',,' in fact or '( ' in fact or ' )' in fact:
            issues.append("Leere oder ungültige Argumente")
        
        # Balancierte Klammern
        if fact.count('(') != fact.count(')'):
            issues.append("Unbalancierte Klammern")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def _validate_chemistry(self, fact: str) -> Dict:
        """
        Validiert Chemie-Fakten
        """
        result = {
            "domain": "CHEMISTRY",
            "passed": True,
            "details": ""
        }
        
        # ChemicalReaction checks
        if fact.startswith("ChemicalReaction"):
            # Prüfe Massenerhaltung (vereinfacht)
            if "CH4" in fact and "2O2" in fact:
                if "CO2" not in fact or "2H2O" not in fact:
                    result["passed"] = False
                    result["details"] = "Methan-Verbrennung: Produkte falsch"
            
            # Prüfe Temperatur-Format
            temp_match = re.search(r'\d+[CK]', fact)
            if not temp_match:
                result["passed"] = False
                result["details"] = "Temperatur fehlt oder falsches Format"
            
            # Prüfe Druck-Format  
            pressure_match = re.search(r'\d+(?:atm|bar|Pa|kPa)', fact)
            if not pressure_match:
                result["passed"] = False
                result["details"] = "Druck fehlt oder falsches Format"
        
        # MolecularStructure checks
        elif fact.startswith("MolecularStructure"):
            # Prüfe bekannte Geometrien
            valid_geometries = ["linear", "bent", "trigonal_planar", "tetrahedral", 
                               "pyramidal", "octahedral", "trigonal_bipyramidal"]
            
            has_valid_geometry = any(geom in fact for geom in valid_geometries)
            if not has_valid_geometry:
                result["passed"] = False
                result["details"] = "Ungültige Molekülgeometrie"
            
            # Prüfe Hybridisierung
            if "sp" not in fact and "sp2" not in fact and "sp3" not in fact:
                result["passed"] = False
                result["details"] = "Hybridisierung fehlt"
        
        return result
    
    def _validate_physics(self, fact: str) -> Dict:
        """
        Validiert Physik-Fakten
        """
        result = {
            "domain": "PHYSICS",
            "passed": True,
            "details": ""
        }
        
        # ElectromagneticWave checks
        if fact.startswith("ElectromagneticWave"):
            # Prüfe c = λν (Wellenlänge * Frequenz = Lichtgeschwindigkeit)
            if "vacuum" in fact and "299792458" not in fact and "3e8" not in fact:
                result["passed"] = False
                result["details"] = "Lichtgeschwindigkeit im Vakuum falsch"
            
            # Prüfe Energie-Einheiten
            if not re.search(r'\d+(?:\.\d+)?(?:eV|keV|MeV|GeV)', fact):
                result["passed"] = False
                result["details"] = "Energie fehlt oder falsche Einheit"
        
        # ParticleInteraction checks
        elif fact.startswith("ParticleInteraction"):
            # Prüfe Kräfte
            valid_forces = ["electromagnetic", "strong_nuclear", "weak_nuclear", "gravity"]
            has_valid_force = any(force in fact for force in valid_forces)
            
            if not has_valid_force:
                result["passed"] = False
                result["details"] = "Ungültige oder fehlende Fundamentalkraft"
            
            # Prüfe Erhaltungssätze
            if "conserved" not in fact and "not_conserved" not in fact:
                result["passed"] = False
                result["details"] = "Erhaltungssatz-Status fehlt"
        
        # Motion checks
        elif fact.startswith("Motion"):
            # Prüfe Erdbeschleunigung
            if "9.8" not in fact and "9.81" not in fact:
                result["passed"] = False
                result["details"] = "Erdbeschleunigung fehlt oder falsch"
        
        return result
    
    def _validate_biology(self, fact: str) -> Dict:
        """
        Validiert Biologie-Fakten
        """
        result = {
            "domain": "BIOLOGY",
            "passed": True,
            "details": ""
        }
        
        # ProteinSynthesis checks
        if fact.startswith("ProteinSynthesis"):
            required = ["gene", "mRNA", "ribosome", "protein"]
            missing = [r for r in required if r not in fact.lower()]
            
            if missing:
                result["passed"] = False
                result["details"] = f"Fehlende Komponenten: {', '.join(missing)}"
            
            # Prüfe Lokalisationen
            valid_locations = ["nucleus", "cytoplasm", "endoplasmic_reticulum", "ER", 
                              "mitochondria", "chloroplast"]
            has_location = any(loc in fact for loc in valid_locations)
            
            if not has_location:
                result["passed"] = False
                result["details"] = "Zelluläre Lokalisation fehlt"
        
        # CellularRespiration checks
        elif fact.startswith("CellularRespiration"):
            # Prüfe Glucose-Formel
            if "glucose" in fact:
                if "6O2" in fact and "6CO2" in fact and "6H2O" in fact:
                    # Aerobe Atmung korrekt
                    if "38ATP" not in fact and "36ATP" not in fact:
                        result["passed"] = False
                        result["details"] = "ATP-Ausbeute falsch (erwartet: 36-38)"
                elif "lactate" in fact or "ethanol" in fact:
                    # Anaerobe Atmung
                    if "2ATP" not in fact:
                        result["passed"] = False
                        result["details"] = "ATP-Ausbeute bei Gärung falsch (erwartet: 2)"
        
        # DNAReplication checks
        elif fact.startswith("DNAReplication"):
            required = ["DNA_polymerase", "primer", "nucleotides"]
            missing = [r for r in required if r not in fact]
            
            if missing:
                result["passed"] = False
                result["details"] = f"Fehlende Replikationskomponenten: {', '.join(missing)}"
        
        return result
    
    def _validate_cs(self, fact: str) -> Dict:
        """
        Validiert Informatik-Fakten
        """
        result = {
            "domain": "COMPUTER_SCIENCE",
            "passed": True,
            "details": ""
        }
        
        # AlgorithmAnalysis checks
        if fact.startswith("AlgorithmAnalysis"):
            # Prüfe Big-O Notation
            if not re.search(r'O\([^)]+\)', fact):
                result["passed"] = False
                result["details"] = "Big-O Notation fehlt"
            
            # Prüfe bekannte Algorithmen
            known_algos = ["quicksort", "mergesort", "heapsort", "binary_search", 
                          "dijkstra", "bellman_ford", "kruskal", "prim"]
            has_known = any(algo in fact.lower() for algo in known_algos)
            
            if not has_known:
                result["passed"] = False
                result["details"] = "Unbekannter Algorithmus"
        
        # TCPConnection checks
        elif fact.startswith("TCPConnection"):
            # Prüfe IP-Format
            ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
            if not re.search(ip_pattern, fact):
                result["passed"] = False
                result["details"] = "IP-Adresse fehlt oder ungültiges Format"
            
            # Prüfe TCP-Flags
            tcp_flags = ["SYN", "ACK", "FIN", "RST", "PSH", "URG"]
            has_flag = any(flag in fact for flag in tcp_flags)
            
            if not has_flag:
                result["passed"] = False
                result["details"] = "TCP-Flags fehlen"
        
        # DataStructure checks
        elif fact.startswith("DataStructure"):
            # Prüfe Zeitkomplexität
            if not re.search(r'O\([^)]+\)', fact):
                result["passed"] = False
                result["details"] = "Zeitkomplexität fehlt"
        
        return result
    
    def _validate_math(self, fact: str) -> Dict:
        """
        Validiert Mathematik-Fakten
        """
        result = {
            "domain": "MATHEMATICS",
            "passed": True,
            "details": ""
        }
        
        # FunctionAnalysis checks
        if fact.startswith("FunctionAnalysis"):
            properties = ["continuous", "differentiable", "integrable", 
                         "monotonic", "bounded", "periodic"]
            has_property = any(prop in fact for prop in properties)
            
            if not has_property:
                result["passed"] = False
                result["details"] = "Mathematische Eigenschaften fehlen"
        
        # MatrixOperation checks
        elif fact.startswith("MatrixOperation"):
            # Prüfe Dimension
            if not re.search(r'\d+x\d+', fact):
                result["passed"] = False
                result["details"] = "Matrix-Dimensionen fehlen"
            
            # Prüfe Operation
            operations = ["multiply", "inverse", "transpose", "determinant", 
                         "eigenvalue", "LU_decomposition"]
            has_op = any(op in fact for op in operations)
            
            if not has_op:
                result["passed"] = False
                result["details"] = "Matrix-Operation fehlt"
        
        # NumberProperty checks
        elif fact.startswith("NumberProperty"):
            # Prüfe auf Zahl
            if not re.search(r'\d+', fact):
                result["passed"] = False
                result["details"] = "Keine Zahl gefunden"
        
        return result
    
    def _check_scientific_plausibility(self, fact: str, domain: str) -> Dict:
        """
        Prüft allgemeine wissenschaftliche Plausibilität
        """
        checks = {
            "conservation_laws": True,
            "units_correct": True,
            "values_plausible": True,
            "references_valid": True
        }
        
        # Prüfe auf unmögliche Werte
        if re.search(r'-\d+K', fact):  # Negative Kelvin
            checks["values_plausible"] = False
        
        if re.search(r'[3-9]\d{8}m/s', fact):  # Überlichtgeschwindigkeit
            checks["values_plausible"] = False
        
        # Prüfe auf fehlende Einheiten bei Zahlen
        numbers_without_units = re.findall(r'(?<![a-zA-Z])\d+(?:\.\d+)?(?![a-zA-Z0-9_])', fact)
        if len(numbers_without_units) > 3:  # Zu viele Zahlen ohne Einheiten
            checks["units_correct"] = False
        
        # Prüfe auf Personen-Physics-Mix (häufiger Fehler)
        physicists = ["Einstein", "Newton", "Bohr", "Heisenberg", "Schrodinger", 
                      "Feynman", "Maxwell", "Planck"]
        for physicist in physicists:
            if physicist in fact and "DevelopedBy" not in fact and "DiscoveredBy" not in fact:
                checks["references_valid"] = False
                break
        
        return checks


def create_strict_validation_prompt(fact: str, domain: str) -> str:
    """
    Erstellt einen strikten Validierungs-Prompt für LLMs
    """
    return f"""
Validate this scientific fact with EXTREME RIGOR:

Fact: {fact}
Domain: {domain}
Expected arguments: 6-7

STRICT VALIDATION CRITERIA:
1. Scientific accuracy: Is this fact scientifically correct?
2. Conservation laws: Are mass/energy/momentum conserved?
3. Units: Are all units present and correct?
4. Values: Are numerical values physically plausible?
5. Structure: Does it follow Predicate(arg1, ..., argN) format?
6. Domain fit: Is this appropriate for {domain}?

RESPOND ONLY WITH VALID JSON:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "issues": ["list", "of", "problems"],
    "domain_check": {{
        "domain": "{domain}",
        "passed": true/false,
        "details": "explanation"
    }},
    "scientific_accuracy": {{
        "conservation_laws": true/false,
        "units_correct": true/false,
        "values_plausible": true/false,
        "references_valid": true/false
    }},
    "corrected_fact": "corrected version or null"
}}

BE EXTREMELY CRITICAL. Reject anything that isn't 100% scientifically accurate.
"""


if __name__ == "__main__":
    # Test-Beispiele
    validator = ScientificFactValidator()
    
    test_facts = [
        ("ChemicalReaction(N2, 3H2, 2NH3, null, Fe_catalyst, 450C, 200atm)", "CHEMISTRY"),
        ("ChemicalReaction(CH4, CO2, H2O, NH3, catalyst, temp, pressure)", "CHEMISTRY"),  # FALSCH
        ("ParticleInteraction(electron, proton, electromagnetic, -13.6eV, conserved, opposite, hydrogen)", "PHYSICS"),
        ("Field(proton, Einstein, momentum, mass, energy, force)", "PHYSICS"),  # FALSCH
        ("AlgorithmAnalysis(quicksort, O(nlogn), O(nlogn), O(n2), O(logn), divide_conquer, unstable)", "COMPUTER_SCIENCE"),
    ]
    
    print("TESTE WISSENSCHAFTLICHEN VALIDATOR")
    print("="*60)
    
    for fact, domain in test_facts:
        print(f"\nFact: {fact[:60]}...")
        print(f"Domain: {domain}")
        
        result = validator.validate_fact(fact, domain)
        
        print(f"Valid: {result['is_valid']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Domain Check: {result['domain_check']['passed']}")
        
        if result['issues']:
            print(f"Issues: {', '.join(result['issues'][:2])}")
        
        print("-"*40)
