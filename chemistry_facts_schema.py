"""
Chemistry Facts Schema for HAK_GAL
===================================
Pragmatic implementation of n-ary chemical facts
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json

@dataclass
class ChemicalCompound:
    """Represents a chemical compound with identifiers"""
    name: str
    formula: str
    smiles: Optional[str] = None
    inchi: Optional[str] = None
    cas_number: Optional[str] = None
    
    def to_fact_arg(self) -> str:
        """Convert to fact argument format"""
        if self.smiles:
            return f"{self.name}[{self.smiles}]"
        return f"{self.name}[{self.formula}]"

@dataclass
class ReactionConditions:
    """Reaction conditions as structured data"""
    temperature_k: Optional[float] = None
    pressure_pa: Optional[float] = None
    solvent: Optional[str] = None
    ph: Optional[float] = None
    time_s: Optional[float] = None
    
    def to_fact_arg(self) -> str:
        """Convert to compact fact representation"""
        parts = []
        if self.temperature_k:
            parts.append(f"T:{self.temperature_k}K")
        if self.pressure_pa:
            parts.append(f"P:{self.pressure_pa}Pa")
        if self.solvent:
            parts.append(f"S:{self.solvent}")
        return f"Conditions[{','.join(parts)}]"

class ChemistryFactGenerator:
    """Generate n-ary chemistry facts for HAK_GAL"""
    
    # Predicate templates with argument counts
    PREDICATES = {
        # 3-argument facts
        'ChemicalReaction': ['reactant', 'product', 'type'],
        'HasFunctionalGroup': ['compound', 'group', 'position'],
        'Isomer': ['compound1', 'compound2', 'type'],
        
        # 4-argument facts  
        'AcidBaseReaction': ['acid', 'base', 'salt', 'water'],
        'Catalysis': ['catalyst', 'substrate', 'product', 'mechanism'],
        'ChemicalProperty': ['compound', 'property', 'value', 'conditions'],
        
        # 5-argument facts
        'Combustion': ['fuel', 'oxidizer', 'CO2', 'H2O', 'energy'],
        'OrganicReaction': ['substrate', 'reagent', 'product', 'mechanism', 'conditions'],
        'Spectroscopy': ['compound', 'technique', 'peak', 'intensity', 'assignment'],
        
        # 6-argument facts
        'MolecularGeometry': ['molecule', 'central_atom', 'ligands', 'shape', 'hybridization', 'angle'],
        'CrystalStructure': ['compound', 'system', 'a', 'b', 'c', 'space_group'],
        'ReactionKinetics': ['reaction', 'rate_constant', 'activation_energy', 'temperature', 'order', 'mechanism'],
        
        # 7-argument facts
        'ChemicalEquilibrium': ['reaction', 'reactant1', 'reactant2', 'product1', 'product2', 'Keq', 'conditions'],
        'ComplexReaction': ['step1', 'step2', 'step3', 'intermediate1', 'intermediate2', 'catalyst', 'yield'],
        'MultiStepSynthesis': ['starting', 'reagent1', 'intermediate', 'reagent2', 'product', 'conditions', 'yield']
    }
    
    def generate_reaction_fact(self, 
                               reactants: List[ChemicalCompound],
                               products: List[ChemicalCompound],
                               conditions: Optional[ReactionConditions] = None,
                               catalyst: Optional[str] = None) -> str:
        """Generate a complete reaction fact"""
        
        # Choose appropriate predicate based on complexity
        if len(reactants) == 2 and len(products) == 2:
            # Use 7-argument ChemicalEquilibrium
            if conditions:
                return f"ChemicalEquilibrium(reaction_{id(self)}, {reactants[0].to_fact_arg()}, {reactants[1].to_fact_arg()}, {products[0].to_fact_arg()}, {products[1].to_fact_arg()}, Keq_unknown, {conditions.to_fact_arg()})."
            else:
                # Use 5-argument version
                return f"ChemicalReaction({reactants[0].to_fact_arg()}, {reactants[1].to_fact_arg()}, {products[0].to_fact_arg()}, {products[1].to_fact_arg()}, standard_conditions)."
        
        # Simpler reaction
        elif len(reactants) == 1 and len(products) == 1:
            if catalyst:
                return f"Catalysis({catalyst}, {reactants[0].to_fact_arg()}, {products[0].to_fact_arg()}, heterogeneous)."
            else:
                return f"ChemicalReaction({reactants[0].to_fact_arg()}, {products[0].to_fact_arg()}, direct)."
        
        # Complex multi-step
        else:
            parts = [r.to_fact_arg() for r in reactants] + [p.to_fact_arg() for p in products]
            if len(parts) <= 7:
                return f"ComplexReaction({', '.join(parts)})."
            else:
                # Truncate to 7 arguments
                return f"ComplexReaction({', '.join(parts[:7])})."
    
    def generate_structure_fact(self, compound: ChemicalCompound, geometry_data: Dict[str, Any]) -> str:
        """Generate molecular structure fact"""
        
        if 'shape' in geometry_data and 'hybridization' in geometry_data:
            return f"MolecularGeometry({compound.to_fact_arg()}, {geometry_data.get('central', 'C')}, {geometry_data.get('ligands', '4H')}, {geometry_data['shape']}, {geometry_data['hybridization']}, {geometry_data.get('angle', '109.5deg')})."
        
        # Fallback to simpler fact
        return f"HasStructure({compound.to_fact_arg()}, {geometry_data.get('shape', 'unknown')})."
    
    def validate_fact(self, fact: str) -> bool:
        """Basic validation of chemical facts"""
        
        # Check basic format
        if not fact.endswith('.'):
            return False
        
        # Check for balanced parentheses
        if fact.count('(') != fact.count(')'):
            return False
        
        # Check argument count limits (max 7 for current schema)
        arg_count = fact.count(',') + 1
        if arg_count > 7:
            print(f"Warning: Fact has {arg_count} arguments, exceeding limit of 7")
            return False
        
        return True

# Example usage
if __name__ == "__main__":
    generator = ChemistryFactGenerator()
    
    # Create compounds
    methane = ChemicalCompound("methane", "CH4", "C")
    oxygen = ChemicalCompound("oxygen", "O2", "O=O")
    co2 = ChemicalCompound("carbon_dioxide", "CO2", "O=C=O")
    water = ChemicalCompound("water", "H2O", "O")
    
    # Generate combustion reaction fact
    conditions = ReactionConditions(temperature_k=298, pressure_pa=101325)
    
    fact1 = generator.generate_reaction_fact(
        reactants=[methane, oxygen],
        products=[co2, water],
        conditions=conditions
    )
    
    print("Generated Chemical Facts:")
    print("=" * 60)
    print(fact1)
    
    # Generate structure fact
    geometry = {
        'shape': 'tetrahedral',
        'hybridization': 'sp3',
        'central': 'C',
        'ligands': '4H',
        'angle': '109.5deg'
    }
    
    fact2 = generator.generate_structure_fact(methane, geometry)
    print(fact2)
    
    # Generate spectroscopy fact
    fact3 = "Spectroscopy(methane[CH4], IR, 3019cm-1, strong, C-H_stretch)."
    print(fact3)
    
    # Validate all facts
    print("\nValidation:")
    for i, fact in enumerate([fact1, fact2, fact3], 1):
        valid = generator.validate_fact(fact)
        print(f"Fact {i}: {'✓' if valid else '✗'} Valid")
