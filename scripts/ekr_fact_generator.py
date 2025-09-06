#!/usr/bin/env python3
"""
Creative EKR Fact Generator for v6_autopilot
Generates complex, extended facts for the knowledge base
"""

import random
from typing import List
from ekr_implementation import EKRParser

class EKRFactGenerator:
    """Generates diverse complex facts using EKR syntax"""
    
    def __init__(self):
        self.parser = EKRParser()
        
        # Templates for different complexity levels
        self.templates = {
            'nary': [
                "Produces({factory}, {product}, {quantity}, {time}, {quality})",
                "Connects({city1}, {city2}, {transport}, {distance}, {duration})",
                "Transforms({input}, {process}, {output}, {energy}, {efficiency})",
                "Regulates({regulator}, {target}, {mechanism}, {strength}, {context})",
            ],
            'typed': [
                "Reaction(catalyst:{catalyst}, substrate:{substrate}, product:{product}, temp:{temp}, pH:{pH})",
                "Transaction(from:{sender}, to:{receiver}, amount:{amount}, date:{date}, status:{status})",
                "Measurement(sensor:{sensor}, value:{value}, unit:{unit}, time:{time}, accuracy:{accuracy})",
                "Process(input:{input}, operation:{operation}, output:{output}, duration:{duration}, cost:{cost})",
            ],
            'formula': [
                'Formula(name:{name}, expr:"{expr}", domain:{domain}, units:{units})',
                'Equation(name:{name}, lhs:"{lhs}", rhs:"{rhs}", domain:{domain})',
                'Law(name:{name}, statement:"{statement}", domain:{domain}, discoverer:{discoverer})',
            ],
            'temporal': [
                "Temporal(fact:{fact}, start:{start}, end:{end}, duration:{duration})",
                "Event(name:{name}, time:{time}, location:{location}, participants:[{participants}])",
                "Period(entity:{entity}, state:{state}, from:{from}, to:{to})",
            ],
            'graph': [
                "Graph(nodes:[{nodes}], edges:[{edges}], type:{type})",
                "Network(components:[{components}], connections:[{connections}], topology:{topology})",
                "Hierarchy(root:{root}, children:[{children}], depth:{depth})",
            ]
        }
        
        # Rich value sets for substitution
        self.values = {
            'factory': ['TeslaGigafactory', 'FoxconnPlant', 'BMWFactory', 'IntelFab'],
            'product': ['ElectricVehicle', 'Microchip', 'SolarPanel', 'Battery'],
            'quantity': ['1000units', '50tons', '10000pieces', '500MW'],
            'time': ['24hours', '7days', '1month', '1quarter'],
            'quality': ['Premium', 'Standard', 'HighGrade', 'Certified'],
            'city1': ['Berlin', 'Tokyo', 'NewYork', 'London', 'Paris'],
            'city2': ['Munich', 'Osaka', 'Boston', 'Manchester', 'Lyon'],
            'transport': ['HighSpeedRail', 'Highway', 'AirRoute', 'SeaRoute'],
            'distance': ['500km', '1000km', '200miles', '50nm'],
            'duration': ['2hours', '5hours', '45minutes', '1day'],
            'catalyst': ['Platinum', 'Palladium', 'Enzyme', 'Nickel'],
            'substrate': ['H2', 'Glucose', 'CO2', 'Methane'],
            'temp': ['25°C', '100°C', '37°C', '-10°C'],
            'pH': ['7.0', '4.5', '9.2', '6.8'],
            'domain': ['Physics', 'Chemistry', 'Biology', 'Mathematics', 'Engineering'],
            'expr': ['E=mc²', 'F=ma', 'PV=nRT', 'a²+b²=c²', 'ΔG=ΔH-TΔS'],
            'fact': ['IsActive(System)', 'HasStatus(Process,Running)', 'Contains(Database,Records)'],
            'start': ['2025-01-01', '2025-08-20T10:00:00', 'Q1-2025'],
            'end': ['2025-12-31', '2025-08-21T18:00:00', 'Q4-2025'],
        }
    
    def generate_nary_fact(self) -> str:
        """Generate n-ary relation with 3-7 arguments"""
        template = random.choice(self.templates['nary'])
        
        # Simple substitution for demo
        fact = template
        for key in self.values:
            if '{' + key + '}' in fact:
                fact = fact.replace('{' + key + '}', random.choice(self.values.get(key, [key])))
        
        # Replace any remaining placeholders
        import re
        remaining = re.findall(r'{(\w+)}', fact)
        for placeholder in remaining:
            fact = fact.replace('{' + placeholder + '}', f'{placeholder.title()}{random.randint(1,100)}')
        
        return fact + '.'
    
    def generate_typed_fact(self) -> str:
        """Generate fact with typed/role arguments"""
        template = random.choice(self.templates['typed'])
        
        fact = template
        for key in self.values:
            if '{' + key + '}' in fact:
                fact = fact.replace('{' + key + '}', random.choice(self.values.get(key, [key])))
        
        # Handle remaining
        import re
        remaining = re.findall(r'{(\w+)}', fact)
        for placeholder in remaining:
            fact = fact.replace('{' + placeholder + '}', f'{placeholder.title()}{random.randint(1,100)}')
        
        return fact + '.'
    
    def generate_formula_fact(self) -> str:
        """Generate mathematical formula fact"""
        template = random.choice(self.templates['formula'])
        
        # Predefined formulas
        formulas = [
            ('NewtonsSecondLaw', 'F=ma', 'Physics', 'N'),
            ('OhmsLaw', 'V=IR', 'Electronics', 'V'),
            ('EinsteinMassEnergy', 'E=mc²', 'Physics', 'J'),
            ('IdealGasLaw', 'PV=nRT', 'Chemistry', 'Pa·m³'),
            ('CoulombsLaw', 'F=k(q₁q₂)/r²', 'Physics', 'N'),
            ('PythagoreanTheorem', 'a²+b²=c²', 'Mathematics', 'units'),
        ]
        
        formula_data = random.choice(formulas)
        fact = template.replace('{name}', formula_data[0])
        fact = fact.replace('{expr}', formula_data[1])
        fact = fact.replace('{domain}', formula_data[2])
        fact = fact.replace('{units}', formula_data[3])
        
        # Handle other placeholders
        fact = fact.replace('{lhs}', formula_data[1].split('=')[0] if '=' in formula_data[1] else 'x')
        fact = fact.replace('{rhs}', formula_data[1].split('=')[1] if '=' in formula_data[1] else 'y')
        fact = fact.replace('{statement}', f'"{formula_data[1]}"')
        fact = fact.replace('{discoverer}', random.choice(['Newton', 'Einstein', 'Ohm', 'Coulomb']))
        
        return fact + '.'
    
    def generate_temporal_fact(self) -> str:
        """Generate temporal/time-bound fact"""
        template = random.choice(self.templates['temporal'])
        
        fact = template
        for key in self.values:
            if '{' + key + '}' in fact:
                fact = fact.replace('{' + key + '}', random.choice(self.values.get(key, [key])))
        
        # Special handling for lists
        fact = fact.replace('[{participants}]', 
                          f'[{",".join(random.sample(["Alice", "Bob", "Charlie", "Diana"], 2))}]')
        fact = fact.replace('[{components}]', 
                          f'[{",".join(random.sample(["Server", "Database", "Cache", "LoadBalancer"], 3))}]')
        
        # Handle remaining
        import re
        remaining = re.findall(r'{(\w+)}', fact)
        for placeholder in remaining:
            fact = fact.replace('{' + placeholder + '}', f'{placeholder.title()}{random.randint(1,100)}')
        
        return fact + '.'
    
    def generate_mixed_batch(self, count: int) -> List[str]:
        """Generate a diverse batch of complex facts"""
        facts = []
        generators = [
            self.generate_nary_fact,
            self.generate_typed_fact,
            self.generate_formula_fact,
            self.generate_temporal_fact,
        ]
        
        for _ in range(count):
            generator = random.choice(generators)
            try:
                fact = generator()
                # Validate it parses
                self.parser.parse(fact)
                facts.append(fact)
            except:
                # If generation fails, add a simple fact
                facts.append(f"IsA(Entity{random.randint(1,1000)}, Class{random.randint(1,100)}).")
        
        return facts
    
    def generate_domain_specific(self, domain: str, count: int) -> List[str]:
        """Generate facts for specific domain"""
        domain_facts = {
            'science': [
                "Reaction(catalyst:Enzyme, substrate:Glucose, product:Fructose, temp:37°C, pH:7.0).",
                "Formula(name:Photosynthesis, expr:\"6CO₂+6H₂O→C₆H₁₂O₆+6O₂\", domain:Biology).",
                "Transforms(Light, Chlorophyll, ChemicalEnergy, 680nm, 3%).",
            ],
            'technology': [
                "Connects(Server1, Database1, TCP, Port5432, 10ms).",
                "Process(input:RawData, operation:MachineLearning, output:Model, duration:2hours, cost:100$).",
                "Graph(nodes:[GPU1,GPU2,GPU3], edges:[{from:GPU1,to:GPU2,bandwidth:100Gbps}], type:ComputeCluster).",
            ],
            'business': [
                "Transaction(from:CompanyA, to:CompanyB, amount:1000000€, date:2025-08-20, status:Completed).",
                "Temporal(fact:Contract(A,B), start:2025-01-01, end:2025-12-31, duration:1year).",
                "DependsOn(ProjectAlpha, [Budget(500k), Team(10engineers), Deadline(Q4-2025)], {priority:critical}).",
            ]
        }
        
        base_facts = domain_facts.get(domain, [])
        result = []
        
        # Repeat and vary the base facts
        for _ in range(count):
            if base_facts:
                fact = random.choice(base_facts)
                # Add slight variations
                fact = fact.replace('1', str(random.randint(1, 10)))
                fact = fact.replace('A', random.choice(['A', 'B', 'C', 'X', 'Y']))
                result.append(fact)
            else:
                # Fallback to mixed generation
                result.extend(self.generate_mixed_batch(1))
        
        return result[:count]


def main():
    """Test the EKR fact generator"""
    generator = EKRFactGenerator()
    
    print("🎨 EKR Fact Generator Test")
    print("=" * 60)
    
    # Generate different types
    print("\n📝 Sample Complex Facts:\n")
    
    print("N-ary Relations:")
    for _ in range(3):
        fact = generator.generate_nary_fact()
        print(f"  • {fact}")
    
    print("\nTyped Arguments:")
    for _ in range(3):
        fact = generator.generate_typed_fact()
        print(f"  • {fact}")
    
    print("\nFormulas:")
    for _ in range(3):
        fact = generator.generate_formula_fact()
        print(f"  • {fact}")
    
    print("\nTemporal Facts:")
    for _ in range(3):
        fact = generator.generate_temporal_fact()
        print(f"  • {fact}")
    
    print("\n" + "=" * 60)
    print("✅ Ready for integration with v6_autopilot!")
    print("\nTo use: Import EKRFactGenerator in v6_autopilot_enhanced.py")


if __name__ == "__main__":
    main()
