"""
WISSENSCHAFTLICH KORREKTE 6-7-ARGUMENT FAKTEN-PATTERNS
Für die Extended Engine zur Generierung sinnvoller komplexer Fakten
"""

VALIDATED_PATTERNS = {
    
    "CHEMISTRY": [
        # Chemische Reaktionen (7 Argumente)
        "ChemicalReaction(CH4, 2O2, CO2, 2H2O, spark, 25C, 1atm)",
        "ChemicalReaction(N2, 3H2, 2NH3, null, Fe_catalyst, 450C, 200atm)",  # Haber-Bosch
        "ChemicalReaction(2H2O2, null, 2H2O, O2, MnO2_catalyst, 20C, 1atm)",
        "ChemicalReaction(CaCO3, heat, CaO, CO2, null, 900C, 1atm)",
        
        # Molekülstruktur (6-7 Argumente)
        "MolecularStructure(CH4, carbon, hydrogen, hydrogen, hydrogen, hydrogen, tetrahedral)",
        "MolecularStructure(H2O, oxygen, hydrogen, hydrogen, null, null, bent)",
        "MolecularStructure(NH3, nitrogen, hydrogen, hydrogen, hydrogen, lone_pair, pyramidal)",
        "MolecularStructure(CO2, carbon, oxygen, oxygen, null, null, linear)",
        
        # Orbital-Konfiguration (6 Argumente)
        "ElectronConfiguration(carbon, 1s2, 2s2, 2p2, null, null, 6_electrons)",
        "ElectronConfiguration(oxygen, 1s2, 2s2, 2p4, null, null, 8_electrons)",
        "ElectronConfiguration(sodium, 1s2, 2s2, 2p6, 3s1, null, 11_electrons)",
    ],
    
    "PHYSICS": [
        # Elektromagnetische Wellen (7 Argumente)
        "ElectromagneticWave(visible_light, 500nm, 600THz, 2.48eV, linear, vacuum, 299792458m/s)",
        "ElectromagneticWave(X-ray, 0.1nm, 3e18Hz, 12.4keV, linear, vacuum, 299792458m/s)",
        "ElectromagneticWave(radio_wave, 1m, 300MHz, 1.24μeV, circular, air, 299700000m/s)",
        
        # Teilchen-Wechselwirkungen (6-7 Argumente)
        "ParticleInteraction(electron, proton, electromagnetic, -13.6eV, conserved, opposite, hydrogen_atom)",
        "ParticleInteraction(proton, proton, strong_nuclear, 2.2MeV, conserved, same, deuteron)",
        "ParticleInteraction(neutron, proton, weak_nuclear, 0.782MeV, not_conserved, neutral, beta_decay)",
        
        # Kinematik (6 Argumente)
        "Motion(projectile, 45degrees, 100m/s, 9.8m/s2, 1020m_range, 10.2s_flight, parabolic)",
        "Motion(satellite, circular_orbit, 7.8km/s, 9.8m/s2, 400km_altitude, 90min_period, stable)",
    ],
    
    "BIOLOGY": [
        # Protein-Synthese (7 Argumente)
        "ProteinSynthesis(BRCA1_gene, mRNA, ribosome, tRNA_Met, methionine, BRCA1_protein, cytoplasm)",
        "ProteinSynthesis(insulin_gene, pre-mRNA, ribosome, tRNA_chain, amino_acids, proinsulin, ER)",
        
        # Zellatmung (6-7 Argumente)
        "CellularRespiration(glucose, 6O2, 6CO2, 6H2O, 38ATP, mitochondria, aerobic)",
        "CellularRespiration(glucose, null, 2lactate, null, 2ATP, cytoplasm, anaerobic)",
        
        # Ökosystem-Interaktionen (6-7 Argumente)
        "FoodWeb(grass, rabbit, fox, eagle, bacteria, energy_transfer, grassland)",
        "FoodWeb(phytoplankton, zooplankton, small_fish, shark, decomposer, nutrients, ocean)",
        
        # DNA-Replikation (6 Argumente)
        "DNAReplication(template_strand, DNA_polymerase, primer, nucleotides, 3to5_direction, semiconservative)",
        "DNAReplication(lagging_strand, primase, RNA_primer, Okazaki_fragments, ligase, discontinuous)",
    ],
    
    "COMPUTER_SCIENCE": [
        # Netzwerk-Protokolle (7 Argumente)
        "TCPConnection(192.168.1.1, 8080, 10.0.0.1, 443, SYN, 0x1234, established)",
        "HTTPRequest(GET, /api/data, localhost, 8088, JSON, 200OK, 1.5ms)",
        "DNSQuery(example.com, A_record, 8.8.8.8, recursive, 93.184.216.34, 23ms, cached)",
        
        # Algorithmus-Komplexität (6-7 Argumente)
        "AlgorithmAnalysis(quicksort, O(nlogn), O(nlogn), O(n2), O(logn), divide_conquer, unstable)",
        "AlgorithmAnalysis(binary_search, O(1), O(logn), O(logn), O(1), sorted_array, iterative)",
        "AlgorithmAnalysis(dijkstra, O(V2), O(ElogV), O(ElogV), O(V), priority_queue, greedy)",
        
        # Datenstrukturen (6 Argumente)
        "DataStructure(B-tree, balanced, O(logn), O(logn), O(logn), disk_optimized, database)",
        "DataStructure(hash_table, unordered, O(1), O(1), O(n), collision_chain, cache)",
    ],
    
    "MATHEMATICS": [
        # Funktionen-Analyse (6-7 Argumente)
        "FunctionAnalysis(f(x)=x^2, continuous, differentiable, 2x, 2, convex, parabola)",
        "FunctionAnalysis(sin(x), periodic, continuous, cos(x), -sin(x), bounded, wave)",
        "FunctionAnalysis(e^x, exponential, continuous, e^x, e^x, monotonic, growth)",
        
        # Lineare Algebra (6 Argumente)
        "MatrixOperation(A_3x3, B_3x3, multiply, C_3x3, 27_operations, non_commutative)",
        "MatrixOperation(A_nxn, inverse, determinant, eigenvalues, O(n3), LU_decomposition)",
        
        # Zahlentheorie (6-7 Argumente)
        "NumberProperty(2, prime, even, 1_and_2, binary_10, smallest_prime, unique)",
        "NumberProperty(6, composite, perfect, 1_2_3_6, divisors_sum_6, abundant_false, triangular)",
    ]
}

# Validierungs-Regeln für Patterns
VALIDATION_RULES = {
    "ChemicalReaction": {
        "arg_count": [6, 7],
        "required_positions": {
            0: "reactant1",
            2: "product1_or_null", 
            5: "temperature",
            6: "pressure"
        },
        "constraints": [
            "Temperature must include unit (C, K)",
            "Pressure must include unit (atm, Pa, bar)",
            "Catalyst can be 'null' if none",
            "Mass must be conserved"
        ]
    },
    
    "ParticleInteraction": {
        "arg_count": [6, 7],
        "required_positions": {
            0: "particle1",
            1: "particle2",
            2: "force_type",
            3: "energy",
            4: "momentum_conservation"
        },
        "constraints": [
            "Force must be: electromagnetic, strong_nuclear, weak_nuclear, gravity",
            "Energy must include unit (eV, MeV, GeV)",
            "Momentum: conserved or not_conserved"
        ]
    },
    
    "ProteinSynthesis": {
        "arg_count": [6, 7],
        "required_positions": {
            0: "gene",
            1: "mRNA_type",
            2: "ribosome",
            5: "protein",
            6: "location"
        },
        "constraints": [
            "Location: nucleus, cytoplasm, ER, mitochondria",
            "Gene name must be valid",
            "Protein must match gene function"
        ]
    }
}

# Generator-Prompt-Template für LLMs
GENERATION_PROMPT_TEMPLATE = """
Generate a scientifically accurate fact following this EXACT pattern:

Pattern: {pattern_name}({arg1_desc}, {arg2_desc}, {arg3_desc}, {arg4_desc}, {arg5_desc}, {arg6_desc}, {arg7_desc})

Requirements:
1. The fact MUST be scientifically/technically correct
2. Use EXACTLY {arg_count} arguments
3. Follow the exact order specified
4. Use 'null' for absent values, never skip positions
5. Include units where applicable (C, K, atm, eV, m/s, etc.)
6. Ensure conservation laws are respected (mass, energy, momentum)

Good Examples:
{good_examples}

Bad Examples (DO NOT generate like these):
- Mixing people names with physical quantities
- Random combinations without meaning
- Incorrect chemical formulas
- Violations of physical laws

Generate ONE fact only, no explanation.
Output format: Predicate(arg1, arg2, arg3, arg4, arg5, arg6[, arg7])
"""

# Cleanup-Patterns für existierende fehlerhafte Fakten
CLEANUP_PATTERNS = [
    # Entferne Fakten die Personen mit physikalischen Größen mischen
    "DELETE FROM facts WHERE statement LIKE '%Einstein%' AND statement NOT LIKE '%WasDevelopedBy%'",
    "DELETE FROM facts WHERE statement LIKE '%Newton%' AND statement NOT LIKE '%WasDevelopedBy%'", 
    "DELETE FROM facts WHERE statement LIKE '%Bohr%' AND statement NOT LIKE '%WasDevelopedBy%'",
    
    # Entferne chemisch falsche Kombinationen
    "DELETE FROM facts WHERE statement LIKE 'ConsistsOf(CH4%' AND statement NOT LIKE '%carbon%hydrogen%'",
    "DELETE FROM facts WHERE statement LIKE 'ConsistsOf(H2O%' AND statement NOT LIKE '%hydrogen%oxygen%'",
    "DELETE FROM facts WHERE statement LIKE 'ConsistsOf(CO2%' AND statement NOT LIKE '%carbon%oxygen%'",
    
    # Entferne Fakten ohne klares Prädikat-Pattern
    "DELETE FROM facts WHERE statement LIKE 'DNA(%'",  # DNA ist kein Prädikat
    "DELETE FROM facts WHERE statement LIKE 'Field(%'", # Zu vage
    "DELETE FROM facts WHERE statement LIKE 'Wave(%'",  # Zu vage
    "DELETE FROM facts WHERE statement LIKE 'Matrix(%' AND statement NOT LIKE 'MatrixOperation%'",
]

if __name__ == "__main__":
    # Zeige Beispiele korrekter Patterns
    print("BEISPIELE WISSENSCHAFTLICH KORREKTER 6-7-ARGUMENT FAKTEN")
    print("="*60)
    
    for domain, patterns in VALIDATED_PATTERNS.items():
        print(f"\n{domain}:")
        print("-"*40)
        for pattern in patterns[:3]:  # Zeige erste 3 pro Domain
            arg_count = pattern.count(',') + 1
            print(f"  [{arg_count} Args] {pattern}")
    
    print("\n" + "="*60)
    print("WICHTIG FÜR INTEGRATION:")
    print("1. Diese Patterns in aethelred_extended_fixed.py einbauen")
    print("2. Validation Rules im Governor implementieren")
    print("3. Generation Prompt Template für LLM verwenden")
    print("4. Cleanup-Patterns auf existierende DB anwenden")
