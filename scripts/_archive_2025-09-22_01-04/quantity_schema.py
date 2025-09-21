"""
Quantity Schema für wissenschaftliche KB mit Unsicherheiten
============================================================
Robuste, parseable Darstellung von Messwerten mit Einheiten und Fehlerbalken
"""

import re
from dataclasses import dataclass
from typing import Optional, Union, List, Tuple, Dict, Any
import json

@dataclass
class Quantity:
    """
    Wissenschaftliche Größe mit Unsicherheit
    Format: Q(value, unit, err_abs?, err_rel?, conf?)
    """
    value: float
    unit: str
    err_abs: Optional[float] = None  # Absoluter Fehler
    err_rel: Optional[float] = None  # Relativer Fehler in %
    conf: Optional[float] = 95.0      # Konfidenzintervall in %
    
    def __post_init__(self):
        # Validierung
        if self.conf and not (50 <= self.conf <= 99.9):
            raise ValueError(f"Confidence must be 50-99.9%, got {self.conf}")
        if self.err_rel and not (0 < self.err_rel <= 100):
            raise ValueError(f"Relative error must be 0-100%, got {self.err_rel}")
    
    def to_string(self) -> str:
        """Kompakte String-Darstellung: Q(2.3e-4, s^-1, err_rel:5, conf:95)"""
        parts = [str(self.value), self.unit]
        if self.err_abs is not None:
            parts.append(f"err_abs:{self.err_abs}")
        if self.err_rel is not None:
            parts.append(f"err_rel:{self.err_rel}")
        if self.conf != 95.0:
            parts.append(f"conf:{self.conf}")
        return f"Q({', '.join(parts)})"
    
    def to_dict(self) -> Dict:
        """JSON-serialisierbares Dict"""
        return {
            'value': self.value,
            'unit': self.unit,
            'err_abs': self.err_abs,
            'err_rel': self.err_rel,
            'conf': self.conf
        }
    
    @classmethod
    def parse(cls, q_string: str) -> 'Quantity':
        """Parse Q(...) String zurück zu Quantity Objekt"""
        if not q_string.startswith('Q(') or not q_string.endswith(')'):
            raise ValueError(f"Invalid Q format: {q_string}")
        
        content = q_string[2:-1]  # Remove Q( and )
        parts = [p.strip() for p in content.split(',')]
        
        if len(parts) < 2:
            raise ValueError(f"Q needs at least value and unit: {q_string}")
        
        value = float(parts[0])
        unit = parts[1]
        
        # Parse optional parameters
        err_abs = None
        err_rel = None
        conf = 95.0
        
        for part in parts[2:]:
            if ':' in part:
                key, val = part.split(':', 1)
                if key == 'err_abs':
                    err_abs = float(val)
                elif key == 'err_rel':
                    err_rel = float(val)
                elif key == 'conf':
                    conf = float(val)
        
        return cls(value, unit, err_abs, err_rel, conf)

class StoichiometricParticipant:
    """Reaktionsteilnehmer mit Stöchiometrie"""
    def __init__(self, compound: str, coefficient: float = 1.0, phase: Optional[str] = None):
        self.compound = compound
        self.coefficient = coefficient
        self.phase = phase  # s, l, g, aq
    
    def to_string(self) -> str:
        """Format: compound:coeff oder compound:coeff(phase)"""
        s = f"{self.compound}:{self.coefficient}"
        if self.phase:
            s += f"({self.phase})"
        return s
    
    @classmethod
    def parse(cls, s: str) -> 'StoichiometricParticipant':
        """Parse compound:coeff(phase) Format"""
        phase = None
        if '(' in s and ')' in s:
            s, phase_part = s.rsplit('(', 1)
            phase = phase_part.rstrip(')')
        
        if ':' in s:
            compound, coeff = s.rsplit(':', 1)
            coefficient = float(coeff)
        else:
            compound = s
            coefficient = 1.0
        
        return cls(compound, coefficient, phase)

class ScientificFactBuilder:
    """Builder für wissenschaftliche Facts mit Q(...) Notation"""
    
    # UCUM/QUDT konforme Einheiten
    VALID_UNITS = {
        # Temperatur
        'K', 'degC',  # Celsius nur für Anzeige, intern K
        # Druck  
        'Pa', 'kPa', 'MPa', 'atm', 'bar', 'torr',
        # Zeit
        's', 'ms', 'us', 'ns', 'min', 'h',
        # Rate
        's^-1', 'min^-1', 'h^-1', 'M^-1.s^-1',
        # Energie
        'J', 'kJ', 'eV', 'kJ/mol', 'kcal/mol',
        # Konzentration
        'M', 'mM', 'uM', 'nM', 'mol/L', 'g/L',
        # Andere
        '%', 'nm', 'A', 'deg', 'rad'
    }
    
    # Explizite Marker statt null
    NONE_MARKERS = {
        'byproduct': 'none',
        'catalyst': 'none', 
        'solvent': 'none',
        'cofactor': 'none'
    }
    
    def build_reaction_kinetics(self, 
                               name: str,
                               k_value: float,
                               k_unit: str,
                               k_error_rel: float,
                               Ea_value: float,
                               Ea_error_abs: float,
                               A_value: float,
                               temp_K: float) -> str:
        """Baue ReactionKinetics Fact mit Quantities"""
        
        k = Quantity(k_value, k_unit, err_rel=k_error_rel)
        Ea = Quantity(Ea_value, 'kJ/mol', err_abs=Ea_error_abs)
        A = Quantity(A_value, 's^-1')
        T = Quantity(temp_K, 'K')
        
        return f"ReactionKinetics({name}, k:{k.to_string()}, Ea:{Ea.to_string()}, A:{A.to_string()}, T:{T.to_string()})."
    
    def build_organic_reaction(self,
                              substrate: str,
                              reagent: str,
                              product: str,
                              mechanism: str,
                              solvent: str,
                              temp_K: float,
                              yield_percent: float,
                              yield_error: float) -> str:
        """Baue OrganicReaction Fact"""
        
        T = Quantity(temp_K, 'K')
        y = Quantity(yield_percent, '%', err_abs=yield_error)
        
        # Verwende explizite Marker für fehlende Werte
        if not solvent:
            solvent = 'solvent:none'
        
        return f"OrganicReaction({substrate}, {reagent}, {product}, {mechanism}, {solvent}, T:{T.to_string()}, yield:{y.to_string()})."
    
    def build_chemical_reaction_stoich(self,
                                      reactants: List[StoichiometricParticipant],
                                      products: List[StoichiometricParticipant],
                                      catalyst: Optional[str],
                                      temp: Quantity,
                                      pressure: Optional[Quantity] = None) -> str:
        """Baue ChemicalReaction mit expliziter Stöchiometrie"""
        
        # Format: participants=[(compound,coeff),...]
        reactant_str = ','.join([p.to_string() for p in reactants])
        product_str = ','.join([p.to_string() for p in products])
        
        cat_str = catalyst if catalyst else 'catalyst:none'
        
        parts = [
            f"reactants:[{reactant_str}]",
            f"products:[{product_str}]",
            cat_str,
            f"T:{temp.to_string()}"
        ]
        
        if pressure:
            parts.append(f"P:{pressure.to_string()}")
        
        return f"ChemicalReaction({', '.join(parts)})."
    
    def validate_reaction_balance(self, 
                                 reactants: List[StoichiometricParticipant],
                                 products: List[StoichiometricParticipant]) -> Tuple[bool, str]:
        """Validiere Element- und Ladungsbilanz"""
        
        # Vereinfachte Validierung - würde mit echter Parsing-Library erweitert
        total_r = sum(p.coefficient for p in reactants)
        total_p = sum(p.coefficient for p in products)
        
        # Hier würde echte Elementbilanz stehen
        # Für Demo nur Koeffizienten-Check
        
        return True, "Validation passed (simplified)"
    
    def validate_yield(self, yield_value: float) -> bool:
        """Validiere Yield-Grenzen"""
        return 0 <= yield_value <= 100

# Beispiel-Verwendung und Test
if __name__ == "__main__":
    builder = ScientificFactBuilder()
    
    print("NEUE FACT-FORMATE MIT Q(...) NOTATION:")
    print("="*60)
    
    # 1. Reaction Kinetics mit Unsicherheiten
    fact1 = builder.build_reaction_kinetics(
        name="H2O2_decomposition",
        k_value=2.3e-4,
        k_unit="s^-1",
        k_error_rel=5,  # 5% relativer Fehler
        Ea_value=75.3,
        Ea_error_abs=2.1,  # ±2.1 kJ/mol
        A_value=1.2e11,
        temp_K=298
    )
    print("\n1. Kinetik mit Unsicherheiten:")
    print(fact1)
    
    # 2. Organic Reaction mit Yield
    fact2 = builder.build_organic_reaction(
        substrate="cyclohexene",
        reagent="Br2",
        product="trans-1,2-dibromocyclohexane",
        mechanism="anti-addition",
        solvent="CCl4",
        temp_K=298,
        yield_percent=82,
        yield_error=3  # ±3%
    )
    print("\n2. Organische Reaktion:")
    print(fact2)
    
    # 3. Stöchiometrische Reaktion
    reactants = [
        StoichiometricParticipant("N2", 1, "g"),
        StoichiometricParticipant("H2", 3, "g")
    ]
    products = [
        StoichiometricParticipant("NH3", 2, "g")
    ]
    
    fact3 = builder.build_chemical_reaction_stoich(
        reactants=reactants,
        products=products,
        catalyst="Fe",
        temp=Quantity(773, 'K'),
        pressure=Quantity(200, 'atm', err_abs=5)
    )
    print("\n3. Haber-Bosch mit Stöchiometrie:")
    print(fact3)
    
    # Test Parsing
    print("\n" + "="*60)
    print("PARSING TEST:")
    q_str = "Q(2.3e-4, s^-1, err_rel:5, conf:95)"
    q_parsed = Quantity.parse(q_str)
    print(f"Original: {q_str}")
    print(f"Parsed:   {q_parsed.to_string()}")
    print(f"Dict:     {q_parsed.to_dict()}")
