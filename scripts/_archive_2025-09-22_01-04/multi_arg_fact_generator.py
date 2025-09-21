#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MULTI-ARGUMENT FACT GENERATOR ENGINE
=====================================
Enhanced fact generation with 3-7 argument support
Integrated with HAK/GAL hexagonal architecture
"""

import os
import sys
import random
import json
import time
import logging
import requests
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Add paths for imports
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL")
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal")

# Constants
AUTH_TOKEN = "515f57956e7bd15ddc3817573598f190"
API_PORT = 5002
API_URL = f"http://localhost:{API_PORT}/api/facts"

class FactComplexity(Enum):
    """Fact complexity levels by argument count"""
    SIMPLE = 2      # Traditional subject-object
    MODERATE = 3    # Location, transfer
    COMPLEX = 4     # Reactions, processes
    ADVANCED = 5    # Detailed processes
    EXPERT = 6      # Molecular geometry
    EXTREME = 7     # Full specification


@dataclass
class FactTemplate:
    """Template for generating multi-argument facts"""
    predicate: str
    arg_count: int
    arg_names: List[str]
    examples: List[List[str]]
    domain: str
    description: str
    complexity: FactComplexity
    
    def generate_random(self) -> str:
        """Generate a random fact from this template"""
        args = random.choice(self.examples)
        return f"{self.predicate}({', '.join(args)})."
    
    def generate_variation(self, base_args: List[str]) -> str:
        """Generate a variation of the given arguments"""
        # Modify one or two arguments randomly
        new_args = base_args.copy()
        num_changes = random.randint(1, min(2, len(new_args)))
        
        for _ in range(num_changes):
            idx = random.randint(0, len(new_args) - 1)
            # Get a different example and use its argument at this position
            other_example = random.choice(self.examples)
            if other_example != base_args:
                new_args[idx] = other_example[idx]
        
        return f"{self.predicate}({', '.join(new_args)})."


class MultiArgFactGenerator:
    """
    Generator for multi-argument facts (3-7 arguments)
    Designed to work with HAK/GAL hexagonal architecture
    """
    
    def __init__(self, auth_token: str = AUTH_TOKEN):
        """Initialize the multi-argument fact generator"""
        self.auth_token = auth_token
        self.api_url = API_URL
        self.templates = self._initialize_templates()
        self.generated_count = 0
        self.session_facts = set()  # Track facts generated in this session
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _initialize_templates(self) -> List[FactTemplate]:
        """Initialize all fact templates (3-7 arguments)"""
        templates = []
        
        # 3-ARGUMENT TEMPLATES
        templates.extend([
            FactTemplate(
                predicate="Located",
                arg_count=3,
                arg_names=["entity", "city", "country"],
                examples=[
                    ["EiffelTower", "Paris", "France"],
                    ["BrandenburgGate", "Berlin", "Germany"],
                    ["Colosseum", "Rome", "Italy"],
                    ["SagradaFamilia", "Barcelona", "Spain"],
                    ["TajMahal", "Agra", "India"],
                    ["OperaHouse", "Sydney", "Australia"],
                    ["ChristRedeemer", "RioDeJaneiro", "Brazil"],
                    ["BigBen", "London", "UK"],
                    ["StatueOfLiberty", "NewYork", "USA"],
                    ["ForbiddenCity", "Beijing", "China"]
                ],
                domain="geography",
                description="Geographic location with city and country",
                complexity=FactComplexity.MODERATE
            ),
            FactTemplate(
                predicate="ChemicalReaction",
                arg_count=3,
                arg_names=["reactant1", "reactant2", "product"],
                examples=[
                    ["H2", "O2", "H2O"],
                    ["Na", "Cl2", "NaCl"],
                    ["Fe", "S", "FeS"],
                    ["Mg", "O2", "MgO"],
                    ["C", "O2", "CO2"],
                    ["N2", "H2", "NH3"],
                    ["S", "O2", "SO2"],
                    ["P4", "O2", "P4O10"],
                    ["Al", "O2", "Al2O3"],
                    ["Cu", "S", "CuS"]
                ],
                domain="chemistry",
                description="Simple chemical reaction",
                complexity=FactComplexity.MODERATE
            ),
            FactTemplate(
                predicate="DataFlow",
                arg_count=3,
                arg_names=["source", "protocol", "destination"],
                examples=[
                    ["ClientApp", "HTTPS", "WebServer"],
                    ["Database", "TCP", "CacheServer"],
                    ["Sensor", "MQTT", "IoTGateway"],
                    ["MobileApp", "REST", "APIServer"],
                    ["Browser", "WebSocket", "RealtimeServer"],
                    ["Microservice", "gRPC", "LoadBalancer"],
                    ["CDN", "HTTP2", "EdgeServer"],
                    ["Queue", "AMQP", "Worker"],
                    ["Logger", "UDP", "LogServer"],
                    ["Metrics", "StatsD", "Monitor"]
                ],
                domain="technology",
                description="Data flow in systems",
                complexity=FactComplexity.MODERATE
            )
        ])
        
        # 4-ARGUMENT TEMPLATES
        templates.extend([
            FactTemplate(
                predicate="AcidBaseReaction",
                arg_count=4,
                arg_names=["acid", "base", "salt", "water"],
                examples=[
                    ["HCl", "NaOH", "NaCl", "H2O"],
                    ["H2SO4", "KOH", "K2SO4", "H2O"],
                    ["HNO3", "Ca(OH)2", "Ca(NO3)2", "H2O"],
                    ["CH3COOH", "NaOH", "CH3COONa", "H2O"],
                    ["H3PO4", "LiOH", "Li3PO4", "H2O"],
                    ["HBr", "KOH", "KBr", "H2O"],
                    ["HI", "NaOH", "NaI", "H2O"],
                    ["HClO4", "NH4OH", "NH4ClO4", "H2O"],
                    ["H2CO3", "NaOH", "Na2CO3", "H2O"],
                    ["HCOOH", "KOH", "HCOOK", "H2O"]
                ],
                domain="chemistry",
                description="Acid-base neutralization",
                complexity=FactComplexity.COMPLEX
            ),
            FactTemplate(
                predicate="EnergyTransfer",
                arg_count=4,
                arg_names=["source", "mechanism", "amount", "target"],
                examples=[
                    ["Sun", "Radiation", "1361W/m2", "Earth"],
                    ["Engine", "Combustion", "2000kJ", "Wheels"],
                    ["Battery", "Electric", "100Wh", "Motor"],
                    ["Laser", "Photon", "5mW", "Detector"],
                    ["Heater", "Convection", "1500W", "Room"],
                    ["Turbine", "Mechanical", "10MW", "Generator"],
                    ["Reactor", "Nuclear", "1000MW", "Grid"],
                    ["Panel", "Photovoltaic", "300W", "Inverter"],
                    ["Coil", "Induction", "50W", "Device"],
                    ["Antenna", "Electromagnetic", "10dBm", "Receiver"]
                ],
                domain="physics",
                description="Energy transfer mechanisms",
                complexity=FactComplexity.COMPLEX
            )
        ])
        
        # 5-ARGUMENT TEMPLATES
        templates.extend([
            FactTemplate(
                predicate="Combustion",
                arg_count=5,
                arg_names=["fuel", "oxidizer", "product1", "product2", "conditions"],
                examples=[
                    ["CH4", "O2", "CO2", "H2O", "T:298K"],
                    ["C2H6", "O2", "CO2", "H2O", "P:1atm"],
                    ["C3H8", "O2", "CO2", "H2O", "catalyst:Pt"],
                    ["C8H18", "O2", "CO2", "H2O", "spark:required"],
                    ["H2", "O2", "H2O", "none", "T:500K"],
                    ["C2H4", "O2", "CO2", "H2O", "flame:blue"],
                    ["C6H14", "O2", "CO2", "H2O", "octane:87"],
                    ["CH3OH", "O2", "CO2", "H2O", "lambda:1.0"],
                    ["C2H2", "O2", "CO2", "H2O", "T:3000K"],
                    ["C4H10", "O2", "CO2", "H2O", "excess_air:20%"]
                ],
                domain="chemistry",
                description="Combustion reactions",
                complexity=FactComplexity.ADVANCED
            ),
            FactTemplate(
                predicate="BiologicalProcess",
                arg_count=5,
                arg_names=["organism", "process", "substrate", "product", "location"],
                examples=[
                    ["Bacteria", "Fermentation", "Glucose", "Ethanol", "Cytoplasm"],
                    ["Plant", "Photosynthesis", "CO2", "Glucose", "Chloroplast"],
                    ["Human", "Respiration", "Glucose", "ATP", "Mitochondria"],
                    ["Yeast", "Glycolysis", "Glucose", "Pyruvate", "Cytoplasm"],
                    ["Liver", "Gluconeogenesis", "Pyruvate", "Glucose", "Hepatocyte"],
                    ["Muscle", "Glycogenolysis", "Glycogen", "Glucose", "Sarcoplasm"],
                    ["Adipocyte", "Lipolysis", "Triglyceride", "FattyAcid", "Cytoplasm"],
                    ["Neuron", "Transmission", "Glutamate", "Signal", "Synapse"],
                    ["RBC", "OxygenTransport", "O2", "Oxyhemoglobin", "Bloodstream"],
                    ["Kidney", "Filtration", "Blood", "Urine", "Nephron"]
                ],
                domain="biology",
                description="Biological processes",
                complexity=FactComplexity.ADVANCED
            ),
            FactTemplate(
                predicate="NetworkPacket",
                arg_count=5,
                arg_names=["source_ip", "dest_ip", "protocol", "port", "payload_size"],
                examples=[
                    ["192.168.1.1", "10.0.0.1", "TCP", "443", "1500bytes"],
                    ["172.16.0.1", "8.8.8.8", "UDP", "53", "512bytes"],
                    ["10.0.0.5", "192.168.2.10", "ICMP", "0", "64bytes"],
                    ["2001:db8::1", "2001:db8::2", "TCP", "80", "9000bytes"],
                    ["127.0.0.1", "127.0.0.1", "TCP", "3306", "4096bytes"],
                    ["10.1.1.1", "10.2.2.2", "UDP", "5060", "256bytes"],
                    ["172.31.0.1", "172.31.0.255", "UDP", "67", "300bytes"],
                    ["fe80::1", "ff02::1", "ICMPv6", "0", "128bytes"],
                    ["203.0.113.1", "198.51.100.1", "TCP", "22", "2048bytes"],
                    ["100.64.0.1", "100.64.0.2", "GRE", "0", "1400bytes"]
                ],
                domain="networking",
                description="Network packet information",
                complexity=FactComplexity.ADVANCED
            )
        ])
        
        # 6-ARGUMENT TEMPLATES
        templates.extend([
            FactTemplate(
                predicate="MolecularGeometry",
                arg_count=6,
                arg_names=["molecule", "central_atom", "ligand", "shape", "hybridization", "angle"],
                examples=[
                    ["CH4", "carbon", "hydrogen", "tetrahedral", "sp3", "angle:109.5deg"],
                    ["NH3", "nitrogen", "hydrogen", "pyramidal", "sp3", "angle:107deg"],
                    ["H2O", "oxygen", "hydrogen", "bent", "sp3", "angle:104.5deg"],
                    ["BF3", "boron", "fluorine", "planar", "sp2", "angle:120deg"],
                    ["SF6", "sulfur", "fluorine", "octahedral", "sp3d2", "angle:90deg"],
                    ["PCl5", "phosphorus", "chlorine", "bipyramidal", "sp3d", "angle:90_120deg"],
                    ["XeF4", "xenon", "fluorine", "square_planar", "sp3d2", "angle:90deg"],
                    ["CO2", "carbon", "oxygen", "linear", "sp", "angle:180deg"],
                    ["SO2", "sulfur", "oxygen", "bent", "sp2", "angle:119deg"],
                    ["ClF3", "chlorine", "fluorine", "T-shaped", "sp3d", "angle:87.5deg"]
                ],
                domain="chemistry",
                description="Molecular geometry details",
                complexity=FactComplexity.EXPERT
            ),
            FactTemplate(
                predicate="CrystalStructure",
                arg_count=6,
                arg_names=["material", "system", "a_axis", "b_axis", "c_axis", "space_group"],
                examples=[
                    ["Diamond", "Cubic", "3.567A", "3.567A", "3.567A", "Fd3m"],
                    ["Graphite", "Hexagonal", "2.461A", "2.461A", "6.708A", "P63/mmc"],
                    ["NaCl", "Cubic", "5.640A", "5.640A", "5.640A", "Fm3m"],
                    ["Quartz", "Hexagonal", "4.914A", "4.914A", "5.405A", "P3121"],
                    ["Iron", "Cubic", "2.866A", "2.866A", "2.866A", "Im3m"],
                    ["Gold", "Cubic", "4.078A", "4.078A", "4.078A", "Fm3m"],
                    ["Copper", "Cubic", "3.615A", "3.615A", "3.615A", "Fm3m"],
                    ["Zinc", "Hexagonal", "2.665A", "2.665A", "4.947A", "P63/mmc"],
                    ["Silicon", "Cubic", "5.431A", "5.431A", "5.431A", "Fd3m"],
                    ["Titanium", "Hexagonal", "2.951A", "2.951A", "4.683A", "P63/mmc"]
                ],
                domain="materials",
                description="Crystal structure parameters",
                complexity=FactComplexity.EXPERT
            )
        ])
        
        # 7-ARGUMENT TEMPLATES
        templates.extend([
            FactTemplate(
                predicate="Motion",
                arg_count=7,
                arg_names=["type", "object", "value", "initial", "final", "condition", "framework"],
                examples=[
                    ["escape_velocity", "earth", "11.2km_s", "surface", "infinity", "no_return", "classical"],
                    ["orbital_velocity", "ISS", "7.66km_s", "circular", "400km_alt", "stable", "newtonian"],
                    ["terminal_velocity", "raindrop", "9m_s", "free_fall", "equilibrium", "air_drag", "fluid"],
                    ["relativistic", "electron", "0.9c", "rest", "lorentz:2.3", "accelerator", "special"],
                    ["quantum_tunnel", "alpha", "5MeV", "nucleus", "escaped", "barrier:30MeV", "quantum"],
                    ["drift_velocity", "electron", "0.1mm_s", "conductor", "steady", "E:100V_m", "ohmic"],
                    ["wave_velocity", "tsunami", "700km_h", "deep_ocean", "shallow", "depth:4000m", "wave"],
                    ["sound_velocity", "air", "343m_s", "source", "receiver", "T:20C", "acoustic"],
                    ["group_velocity", "light", "0.5c", "medium", "dispersive", "n:1.5", "optical"],
                    ["phase_velocity", "wave", "1.2c", "waveguide", "cutoff", "mode:TE10", "electromagnetic"]
                ],
                domain="physics",
                description="Complex motion parameters",
                complexity=FactComplexity.EXTREME
            ),
            FactTemplate(
                predicate="ChemicalEquilibrium",
                arg_count=7,
                arg_names=["name", "reactant1", "reactant2", "product1", "product2", "Keq", "conditions"],
                examples=[
                    ["Haber", "N2", "3H2", "2NH3", "heat", "Keq:0.5", "T:450C_P:200atm"],
                    ["Water", "H2O", "H+", "OH-", "none", "Kw:1e-14", "T:25C"],
                    ["Ester", "RCOOH", "ROH", "RCOOR", "H2O", "Keq:4.0", "catalyst:H2SO4"],
                    ["NO2_dimer", "2NO2", "none", "N2O4", "none", "Keq:8.7", "T:298K"],
                    ["PCl5_dissoc", "PCl5", "none", "PCl3", "Cl2", "Keq:0.04", "T:523K"],
                    ["SO3_form", "2SO2", "O2", "2SO3", "heat", "Keq:100", "catalyst:V2O5"],
                    ["CO_shift", "CO", "H2O", "CO2", "H2", "Keq:10", "T:700K"],
                    ["Methanol", "CO", "2H2", "CH3OH", "heat", "Keq:2.2", "P:50bar_T:250C"],
                    ["Ammonia_decomp", "2NH3", "none", "N2", "3H2", "Keq:2.0", "T:500C"],
                    ["Boudouard", "2CO", "none", "C", "CO2", "Keq:0.1", "T:700C"]
                ],
                domain="chemistry",
                description="Chemical equilibrium systems",
                complexity=FactComplexity.EXTREME
            ),
            FactTemplate(
                predicate="QuantumState",
                arg_count=7,
                arg_names=["particle", "n", "l", "ml", "ms", "energy", "wavefunction"],
                examples=[
                    ["electron", "1", "0", "0", "0.5", "-13.6eV", "1s"],
                    ["electron", "2", "1", "0", "-0.5", "-3.4eV", "2p"],
                    ["electron", "3", "2", "1", "0.5", "-1.51eV", "3d"],
                    ["electron", "4", "3", "2", "-0.5", "-0.85eV", "4f"],
                    ["electron", "2", "0", "0", "0.5", "-3.4eV", "2s"],
                    ["electron", "3", "1", "-1", "-0.5", "-1.51eV", "3p"],
                    ["electron", "4", "2", "0", "0.5", "-0.85eV", "4d"],
                    ["electron", "5", "0", "0", "-0.5", "-0.54eV", "5s"],
                    ["electron", "3", "2", "-2", "0.5", "-1.51eV", "3d"],
                    ["electron", "4", "1", "1", "-0.5", "-0.85eV", "4p"]
                ],
                domain="quantum",
                description="Quantum state specifications",
                complexity=FactComplexity.EXTREME
            )
        ])
        
        return templates
    
    def get_random_template(self, min_args: int = 3, max_args: int = 7) -> FactTemplate:
        """Get a random template within the specified argument range"""
        valid_templates = [
            t for t in self.templates 
            if min_args <= t.arg_count <= max_args
        ]
        return random.choice(valid_templates)
    
    def generate_fact_batch(self, 
                           count: int = 10, 
                           min_args: int = 3, 
                           max_args: int = 7) -> List[str]:
        """Generate a batch of diverse multi-argument facts"""
        facts = []
        
        for _ in range(count):
            template = self.get_random_template(min_args, max_args)
            fact = template.generate_random()
            
            # Avoid duplicates in this session
            attempts = 0
            while fact in self.session_facts and attempts < 10:
                fact = template.generate_random()
                attempts += 1
            
            if fact not in self.session_facts:
                facts.append(fact)
                self.session_facts.add(fact)
        
        return facts
    
    def add_fact_to_kb(self, fact: str, template: FactTemplate = None) -> bool:
        """Add a single fact to the knowledge base via API"""
        try:
            # Extract predicate and args count from fact if template not provided
            if template is None:
                predicate = fact.split('(')[0]
                args = fact.split('(')[1].rstrip(').').split(', ')
                arg_count = len(args)
                domain = "unknown"
            else:
                predicate = template.predicate
                arg_count = template.arg_count
                domain = template.domain
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.auth_token
            }
            
            data = {
                'statement': fact,
                'context': {
                    'source': 'MultiArgFactGenerator',
                    'predicate': predicate,
                    'argCount': arg_count,
                    'domain': domain,
                    'confidence': 0.95,
                    'generator': 'v2.0'
                }
            }
            
            response = requests.post(self.api_url, json=data, headers=headers, timeout=5)
            
            if response.status_code in [200, 201]:
                self.generated_count += 1
                self.logger.info(f"✅ Added: {fact[:80]}...")
                return True
            elif response.status_code == 409:
                self.logger.debug(f"⚠️ Duplicate: {fact[:80]}...")
                return False
            else:
                self.logger.error(f"❌ Failed ({response.status_code}): {fact[:80]}...")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding fact: {e}")
            return False
    
    def run(self, duration_minutes: float = 5.0, facts_per_batch: int = 10):
        """Run the generator for a specified duration"""
        self.logger.info("=" * 60)
        self.logger.info("MULTI-ARGUMENT FACT GENERATOR v2.0")
        self.logger.info(f"Duration: {duration_minutes} minutes")
        self.logger.info(f"Batch size: {facts_per_batch} facts")
        self.logger.info(f"API: {self.api_url}")
        self.logger.info("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        batch_count = 0
        success_count = 0
        
        # Distribution tracking
        complexity_counts = {i: 0 for i in range(3, 8)}
        
        while time.time() < end_time:
            batch_count += 1
            
            # Vary the complexity for this batch
            min_args = random.choice([3, 4, 5])
            max_args = min(min_args + 2, 7)
            
            self.logger.info(f"\n--- Batch {batch_count} ({min_args}-{max_args} args) ---")
            
            # Generate batch
            facts = self.generate_fact_batch(
                count=facts_per_batch,
                min_args=min_args,
                max_args=max_args
            )
            
            # Add to KB
            batch_success = 0
            for fact in facts:
                # Find the template for this fact
                predicate = fact.split('(')[0]
                template = next((t for t in self.templates if t.predicate == predicate), None)
                
                if self.add_fact_to_kb(fact, template):
                    batch_success += 1
                    if template:
                        complexity_counts[template.arg_count] += 1
            
            success_count += batch_success
            
            # Progress report
            elapsed = (time.time() - start_time) / 60
            rate = success_count / elapsed if elapsed > 0 else 0
            
            self.logger.info(f"Batch complete: {batch_success}/{facts_per_batch} added")
            self.logger.info(f"Total: {success_count} facts, Rate: {rate:.1f} facts/min")
            
            # Sleep between batches
            if time.time() < end_time:
                time.sleep(2)
        
        # Final report
        total_time = (time.time() - start_time) / 60
        final_rate = success_count / total_time if total_time > 0 else 0
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("GENERATION COMPLETE")
        self.logger.info(f"Total facts added: {success_count}")
        self.logger.info(f"Time: {total_time:.1f} minutes")
        self.logger.info(f"Rate: {final_rate:.1f} facts/minute")
        self.logger.info(f"Batches: {batch_count}")
        self.logger.info("\nComplexity distribution:")
        for args, count in complexity_counts.items():
            self.logger.info(f"  {args} args: {count} facts")
        self.logger.info("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Argument Fact Generator")
    parser.add_argument("-d", "--duration", type=float, default=5.0,
                       help="Duration in minutes (default: 5.0)")
    parser.add_argument("-b", "--batch", type=int, default=10,
                       help="Facts per batch (default: 10)")
    parser.add_argument("-t", "--token", type=str, default=AUTH_TOKEN,
                       help="Auth token for API")
    args = parser.parse_args()
    
    # Create and run generator
    generator = MultiArgFactGenerator(auth_token=args.token)
    generator.run(duration_minutes=args.duration, facts_per_batch=args.batch)


if __name__ == "__main__":
    main()
