"""
Allgemeine Wissenschaftliche Knowledge Base - Architektur
==========================================================
Multi-Domain n-ary Facts System
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import json

class ScientificDomain(Enum):
    """Wissenschaftliche Domänen"""
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    MATHEMATICS = "mathematics"
    COMPUTER_SCIENCE = "computer_science"
    MEDICINE = "medicine"
    NEUROSCIENCE = "neuroscience"
    GEOLOGY = "geology"
    ASTRONOMY = "astronomy"
    ENGINEERING = "engineering"

@dataclass
class ScientificFact:
    """Strukturierter wissenschaftlicher Fact"""
    predicate: str
    arguments: List[Any]
    domain: ScientificDomain
    arity: int
    confidence: float = 0.8
    source: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        self.arity = len(self.arguments)
        if self.arity < 3 or self.arity > 10:
            raise ValueError(f"Facts müssen 3-10 Argumente haben, nicht {self.arity}")
    
    def to_string(self) -> str:
        """Konvertiere zu Fact-String"""
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"{self.predicate}({args_str})."
    
    def validate(self) -> Tuple[bool, str]:
        """Validiere wissenschaftliche Korrektheit"""
        # Hier würde GPT-5 eingebunden werden
        return True, "Valid"

class TaskDistributor:
    """Verteile Aufgaben zwischen Claude und GPT-5/Max"""
    
    def __init__(self):
        self.tasks_for_claude = []
        self.tasks_for_gpt5 = []
    
    def distribute_tasks(self, request: str) -> Dict[str, List[str]]:
        """
        Verteile Aufgaben basierend auf Komplexität und Anforderungen
        
        Claude (lokal, schnell):
        - Schema-Management
        - Strukturierung
        - Datenbank-Operationen
        - Einfache Validierung
        
        GPT-5/Max (powerful, domain expert):
        - Fact-Generierung
        - Wissenschaftliche Validierung
        - Komplexe Reasoning
        - Literatur-Referenzen
        """
        
        tasks = {
            "claude": [],
            "gpt5": []
        }
        
        # Analysiere Request
        if "generate" in request.lower() or "create" in request.lower():
            tasks["gpt5"].append({
                "type": "generate_facts",
                "instruction": f"Generate scientifically accurate n-ary facts for: {request}",
                "expected_output": "List of facts with 3-10 arguments",
                "validation_required": True
            })
            
            tasks["claude"].append({
                "type": "structure_facts",
                "instruction": "Structure and store generated facts in DB",
                "dependency": "gpt5_output"
            })
        
        elif "validate" in request.lower():
            tasks["gpt5"].append({
                "type": "validate_science",
                "instruction": f"Validate scientific accuracy of: {request}",
                "expected_output": "Validation report with corrections"
            })
        
        elif "expand" in request.lower():
            # Erweitere 2-arg Facts zu n-arg Facts
            tasks["claude"].append({
                "type": "identify_expandable",
                "instruction": "Find facts that can be expanded"
            })
            
            tasks["gpt5"].append({
                "type": "expand_facts",
                "instruction": "Expand simple facts to n-ary with full context",
                "example": "IsA(Water, Molecule) → MolecularStructure(H2O, bent, O, 2H, 104.5deg, sp3, polar)"
            })
        
        return tasks

class ScientificFactGenerator:
    """Generator für verschiedene wissenschaftliche Domänen"""
    
    # Templates für verschiedene Domänen und Aritäten
    TEMPLATES = {
        ScientificDomain.PHYSICS: {
            3: ["Force({object}, {magnitude}N, {direction})",
                "Energy({system}, {value}J, {type})"],
            5: ["Motion({object}, {position}, {velocity}, {acceleration}, {time})",
                "Wave({type}, {frequency}Hz, {wavelength}m, {amplitude}, {medium})"],
            7: ["Collision({object1}, {mass1}kg, {velocity1}m/s, {object2}, {mass2}kg, {velocity2}m/s, {outcome})"]
        },
        
        ScientificDomain.BIOLOGY: {
            4: ["GeneExpression({gene}, {transcript}, {protein}, {regulation})",
                "Mutation({gene}, {position}, {change}, {effect})"],
            6: ["SignalPathway({ligand}, {receptor}, {cascade1}, {cascade2}, {transcription_factor}, {response})"],
            8: ["Photosynthesis({light}, {H2O}, {CO2}, {chlorophyll}, {ATP}, {NADPH}, {glucose}, {O2})"]
        },
        
        ScientificDomain.NEUROSCIENCE: {
            5: ["NeuralCircuit({input}, {neuron1}, {neuron2}, {neuron3}, {output})"],
            7: ["SynapticPlasticity({pre_neuron}, {post_neuron}, {neurotransmitter}, {receptor}, {Ca2+}, {kinase}, {LTP/LTD})"],
            9: ["CognitiveProcess({stimulus}, {perception}, {attention}, {working_memory}, {processing}, {decision}, {motor_planning}, {action}, {feedback})"]
        },
        
        ScientificDomain.CHEMISTRY: {
            4: ["Reaction({reactant1}, {reactant2}, {product}, {conditions})"],
            6: ["Catalysis({substrate}, {enzyme}, {ES_complex}, {transition_state}, {product}, {turnover})"],
            7: ["Equilibrium({reactant1}, {reactant2}, {product1}, {product2}, {Keq}, {temp}K, {pressure}Pa)"]
        },
        
        ScientificDomain.MATHEMATICS: {
            3: ["Relation({set1}, {operation}, {set2})"],
            5: ["Function({domain}, {mapping}, {codomain}, {property1}, {property2})"],
            4: ["Proof({theorem}, {method}, {steps}, {QED})"]
        },
        
        ScientificDomain.COMPUTER_SCIENCE: {
            4: ["Algorithm({input}, {process}, {output}, {complexity})"],
            6: ["DataStructure({type}, {operations}, {space}O(n), {insert}O(n), {delete}O(n), {search}O(n))"],
            5: ["NetworkProtocol({layer}, {source}, {destination}, {data}, {checksum})"]
        }
    }
    
    def generate_for_domain(self, domain: ScientificDomain, concept: str, min_arity: int = 3) -> List[ScientificFact]:
        """Generiere Facts für eine Domäne"""
        facts = []
        
        if domain in self.TEMPLATES:
            for arity, templates in self.TEMPLATES[domain].items():
                if arity >= min_arity:
                    for template in templates:
                        # Hier würde GPT-5 die Templates mit echten Werten füllen
                        fact = ScientificFact(
                            predicate=template.split('(')[0],
                            arguments=self._fill_template(template, concept),
                            domain=domain,
                            arity=arity
                        )
                        facts.append(fact)
        
        return facts
    
    def _fill_template(self, template: str, concept: str) -> List[str]:
        """Fülle Template mit Werten (GPT-5 Task)"""
        # Placeholder - würde von GPT-5 gefüllt
        import re
        placeholders = re.findall(r'\{(\w+)\}', template)
        return [f"{concept}_{ph}" for ph in placeholders]

# Aufgaben für GPT-5/Max
GPT5_TASKS = """
# Aufgaben für GPT-5/Max:

## 1. Fact Generation (Priorität: HOCH)
```
Input: Domain=Biology, Concept="CRISPR"
Output: 
- CRISPRMechanism(Cas9, guide_RNA, PAM_sequence, target_DNA, DSB, NHEJ_or_HDR, edited_gene).
- GeneEditing(CRISPR_Cas9, sgRNA, target_gene, cut_site, repair_template, efficiency_percent, off_target_rate).
```

## 2. Fact Validation (Priorität: HOCH)
```
Input: "ProteinFolding(sequence, chaperone, ATP, native_structure)."
Output: "Incomplete - missing: temperature, pH, time. Suggested expansion:
ProteinFolding(sequence, primary, secondary, tertiary, chaperone, ATP, temp_37C, pH_7.4, time_ms, native_structure)."
```

## 3. Cross-Domain Linking (Priorität: MITTEL)
```
Input: Physics fact + Chemistry fact
Output: Linking fact that connects both domains
Example: 
Physics: "Energy(photon, 650nm, 3.06e-19J)"
Chemistry: "ElectronicTransition(chlorophyll, S0, S1, 650nm)"
Link: "PhotochemicalProcess(photon, chlorophyll, excitation, S0_to_S1, energy_transfer, 650nm)."
```

## 4. Literature Mining (Priorität: NIEDRIG)
```
Input: Scientific paper/abstract
Output: Extracted n-ary facts with source references
```
"""

# Export für Integration
if __name__ == "__main__":
    # Test
    generator = ScientificFactGenerator()
    distributor = TaskDistributor()
    
    # Beispiel-Request
    request = "Generate facts about protein synthesis"
    tasks = distributor.distribute_tasks(request)
    
    print("Aufgabenverteilung:")
    print("="*60)
    print("Claude's Aufgaben:")
    for task in tasks["claude"]:
        print(f"  - {task}")
    
    print("\nGPT-5's Aufgaben:")
    for task in tasks["gpt5"]:
        print(f"  - {task}")
    
    # Test Fact Generation
    facts = generator.generate_for_domain(ScientificDomain.BIOLOGY, "protein", min_arity=4)
    print(f"\nGenerierte Facts: {len(facts)}")
    for fact in facts[:3]:
        print(f"  {fact.to_string()}")
