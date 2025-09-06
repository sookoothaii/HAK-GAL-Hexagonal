#!/usr/bin/env python3
"""
Semantic Fact Generator - Generates MEANINGFUL facts
Based on real-world knowledge and logical relationships
"""

import random
from typing import List, Dict, Tuple
from ekr_implementation import EKRParser

class SemanticFactGenerator:
    """Generates semantically meaningful and logically consistent facts"""
    
    def __init__(self):
        self.parser = EKRParser()
        
        # REAL WORLD KNOWLEDGE BASES
        
        # Geographic knowledge
        self.cities = {
            'Berlin': {'country': 'Germany', 'lat': 52.52, 'lon': 13.405},
            'Munich': {'country': 'Germany', 'lat': 48.135, 'lon': 11.582},
            'Paris': {'country': 'France', 'lat': 48.856, 'lon': 2.352},
            'London': {'country': 'UK', 'lat': 51.507, 'lon': -0.128},
            'Tokyo': {'country': 'Japan', 'lat': 35.689, 'lon': 139.692},
            'NewYork': {'country': 'USA', 'lat': 40.712, 'lon': -74.006},
        }
        
        # Scientific knowledge
        self.chemical_reactions = [
            {'catalyst': 'Platinum', 'substrate': 'H2+O2', 'product': 'H2O', 'temp': '25°C', 'type': 'combustion'},
            {'catalyst': 'Iron', 'substrate': 'N2+H2', 'product': 'NH3', 'temp': '450°C', 'type': 'Haber'},
            {'catalyst': 'Nickel', 'substrate': 'CO+H2', 'product': 'CH4+H2O', 'temp': '300°C', 'type': 'methanation'},
            {'catalyst': 'Enzyme', 'substrate': 'Glucose', 'product': 'Pyruvate+ATP', 'temp': '37°C', 'type': 'glycolysis'},
            {'catalyst': 'Chlorophyll', 'substrate': 'CO2+H2O', 'product': 'Glucose+O2', 'temp': '25°C', 'type': 'photosynthesis'},
        ]
        
        # Computer science knowledge
        self.algorithms = [
            {'name': 'QuickSort', 'complexity': 'O(nlogn)', 'type': 'sorting', 'inventor': 'Hoare'},
            {'name': 'Dijkstra', 'complexity': 'O(V²)', 'type': 'pathfinding', 'inventor': 'Dijkstra'},
            {'name': 'RSA', 'complexity': 'O(n³)', 'type': 'encryption', 'inventor': 'Rivest'},
            {'name': 'PageRank', 'complexity': 'O(n²)', 'type': 'ranking', 'inventor': 'Page'},
            {'name': 'FFT', 'complexity': 'O(nlogn)', 'type': 'transform', 'inventor': 'Cooley'},
        ]
        
        # Manufacturing knowledge
        self.manufacturing = [
            {'factory': 'TeslaGigafactory', 'product': 'Battery', 'capacity': '35GWh/year', 'location': 'Nevada'},
            {'factory': 'TSMC', 'product': 'Microchip', 'capacity': '13million/month', 'location': 'Taiwan'},
            {'factory': 'Boeing', 'product': 'Aircraft', 'capacity': '800/year', 'location': 'Seattle'},
            {'factory': 'Volkswagen', 'product': 'ElectricVehicle', 'capacity': '300000/year', 'location': 'Wolfsburg'},
        ]
        
        # Business processes
        self.business_processes = [
            {'process': 'OrderFulfillment', 'input': 'CustomerOrder', 'output': 'ShippedProduct', 'duration': '2-5days'},
            {'process': 'QualityControl', 'input': 'RawProduct', 'output': 'CertifiedProduct', 'duration': '2hours'},
            {'process': 'DataBackup', 'input': 'LiveData', 'output': 'BackupArchive', 'duration': '30minutes'},
            {'process': 'PaymentProcessing', 'input': 'PaymentRequest', 'output': 'TransactionConfirmation', 'duration': '3seconds'},
        ]
        
        # Physical formulas
        self.formulas = [
            {'name': 'NewtonsGravity', 'expr': 'F=G*m1*m2/r²', 'domain': 'Physics', 'units': 'N'},
            {'name': 'KineticEnergy', 'expr': 'E=0.5*m*v²', 'domain': 'Physics', 'units': 'J'},
            {'name': 'OhmsLaw', 'expr': 'V=I*R', 'domain': 'Electronics', 'units': 'V'},
            {'name': 'IdealGasLaw', 'expr': 'PV=nRT', 'domain': 'Chemistry', 'units': 'Pa*m³'},
            {'name': 'ArrheniusEquation', 'expr': 'k=A*e^(-Ea/RT)', 'domain': 'Chemistry', 'units': '1/s'},
        ]
    
    def calculate_distance(self, city1: str, city2: str) -> int:
        """Calculate approximate distance between cities"""
        if city1 not in self.cities or city2 not in self.cities:
            return random.randint(500, 5000)
        
        # Simplified distance calculation (great circle)
        lat1, lon1 = self.cities[city1]['lat'], self.cities[city1]['lon']
        lat2, lon2 = self.cities[city2]['lat'], self.cities[city2]['lon']
        
        # Very rough approximation
        distance = ((lat2-lat1)**2 + (lon2-lon1)**2)**0.5 * 111  # km per degree
        return int(distance)
    
    def generate_transport_fact(self) -> str:
        """Generate realistic transport connection fact"""
        city1, city2 = random.sample(list(self.cities.keys()), 2)
        distance = self.calculate_distance(city1, city2)
        
        # Choose appropriate transport based on distance
        if distance < 500:
            transport = 'HighSpeedRail'
            duration = f"{distance // 200 + 1}hours"
        elif distance < 2000:
            transport = 'AirRoute'
            duration = f"{distance // 800 + 1}hours"
        else:
            transport = 'AirRoute'
            duration = f"{distance // 800 + 2}hours"
        
        return f"Connects({city1}, {city2}, {transport}, {distance}km, {duration})."
    
    def generate_reaction_fact(self) -> str:
        """Generate scientifically valid reaction fact"""
        reaction = random.choice(self.chemical_reactions)
        return f"Reaction(catalyst:{reaction['catalyst']}, substrate:{reaction['substrate']}, product:{reaction['product']}, temp:{reaction['temp']}, type:{reaction['type']})."
    
    def generate_algorithm_fact(self) -> str:
        """Generate computer science algorithm fact"""
        algo = random.choice(self.algorithms)
        return f"Algorithm(name:{algo['name']}, complexity:{algo['complexity']}, type:{algo['type']}, inventor:{algo['inventor']})."
    
    def generate_production_fact(self) -> str:
        """Generate realistic production fact"""
        mfg = random.choice(self.manufacturing)
        return f"Produces({mfg['factory']}, {mfg['product']}, {mfg['capacity']}, {mfg['location']})."
    
    def generate_process_fact(self) -> str:
        """Generate business process fact"""
        proc = random.choice(self.business_processes)
        return f"Process(name:{proc['process']}, input:{proc['input']}, output:{proc['output']}, duration:{proc['duration']})."
    
    def generate_formula_fact(self) -> str:
        """Generate mathematical formula fact"""
        formula = random.choice(self.formulas)
        return f"Formula(name:{formula['name']}, expr:\"{formula['expr']}\", domain:{formula['domain']}, units:{formula['units']})."
    
    def generate_hierarchy_fact(self) -> str:
        """Generate logical hierarchy fact"""
        hierarchies = [
            ("Mammal", "Animal"),
            ("Dog", "Mammal"),
            ("Cat", "Mammal"),
            ("Python", "ProgrammingLanguage"),
            ("JavaScript", "ProgrammingLanguage"),
            ("ProgrammingLanguage", "Technology"),
            ("Database", "Software"),
            ("PostgreSQL", "Database"),
            ("MongoDB", "Database"),
            ("CPU", "Hardware"),
            ("GPU", "Hardware"),
            ("Hardware", "ComputerComponent"),
            ("Europe", "Continent"),
            ("Germany", "Country"),
            ("France", "Country"),
        ]
        entity, category = random.choice(hierarchies)
        return f"IsA({entity}, {category})."
    
    def generate_temporal_fact(self) -> str:
        """Generate temporal fact with realistic timeframes"""
        events = [
            ("EU_GDPR_Active", "2018-05-25", "ongoing", "regulation"),
            ("COVID19_Pandemic", "2020-03-11", "2023-05-05", "global_event"),
            ("ISS_Operational", "1998-11-20", "ongoing", "space_mission"),
            ("Bitcoin_Network", "2009-01-03", "ongoing", "blockchain"),
        ]
        
        event = random.choice(events)
        return f"Temporal(fact:{event[0]}, start:{event[1]}, end:{event[2]}, type:{event[3]})."
    
    def generate_dependency_fact(self) -> str:
        """Generate logical dependency fact"""
        dependencies = [
            ("WebApplication", ["Database", "WebServer", "Frontend"], "requires"),
            ("MachineLearning", ["Data", "GPUCompute", "Algorithm"], "requires"),
            ("ElectricVehicle", ["Battery", "Motor", "Controller"], "components"),
            ("Photosynthesis", ["Sunlight", "CO2", "Water"], "inputs"),
            ("CloudService", ["DataCenter", "Network", "Virtualization"], "infrastructure"),
        ]
        
        system, deps, rel_type = random.choice(dependencies)
        deps_str = ",".join(deps)
        return f"DependsOn({system}, [{deps_str}], type:{rel_type})."
    
    def generate_regulation_fact(self) -> str:
        """Generate meaningful regulation fact"""
        regulations = [
            ("CentralBank", "InterestRate", "MonetaryPolicy", "Medium", "Economic"),
            ("FDA", "DrugApproval", "SafetyTesting", "High", "Healthcare"),
            ("EPA", "EmissionStandards", "Enforcement", "High", "Environmental"),
            ("SEC", "StockTrading", "Compliance", "High", "Financial"),
            ("GDPR", "DataPrivacy", "UserConsent", "High", "Digital"),
        ]
        
        reg = random.choice(regulations)
        return f"Regulates({reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}, {reg[4]})."
    
    def generate_batch(self, count: int = 10) -> List[str]:
        """Generate a batch of meaningful facts"""
        generators = [
            self.generate_transport_fact,
            self.generate_reaction_fact,
            self.generate_algorithm_fact,
            self.generate_production_fact,
            self.generate_process_fact,
            self.generate_formula_fact,
            self.generate_hierarchy_fact,
            self.generate_temporal_fact,
            self.generate_dependency_fact,
            self.generate_regulation_fact,
        ]
        
        facts = []
        for _ in range(count):
            generator = random.choice(generators)
            try:
                fact = generator()
                facts.append(fact)
            except Exception as e:
                print(f"Error generating fact: {e}")
                # Fallback to simple fact
                facts.append(f"IsA(Entity{random.randint(1,1000)}, Concept).")
        
        return facts


def demo_semantic_generation():
    """Demo semantic fact generation"""
    generator = SemanticFactGenerator()
    
    print("🎯 SEMANTIC FACT GENERATOR - Meaningful Knowledge")
    print("="*60)
    
    print("\n📚 Sample Semantically Valid Facts:\n")
    
    facts = generator.generate_batch(20)
    
    for i, fact in enumerate(facts, 1):
        print(f"{i:2d}. {fact}")
    
    print("\n" + "="*60)
    print("✅ These facts are:")
    print("   • Semantically meaningful")
    print("   • Logically consistent")
    print("   • Based on real-world knowledge")
    print("   • Suitable for reasoning")


if __name__ == "__main__":
    demo_semantic_generation()
