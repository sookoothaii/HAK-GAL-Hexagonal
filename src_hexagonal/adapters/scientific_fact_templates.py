"""
Scientific Fact Templates for Professional Knowledge Representation
====================================================================
Based on industry standards from:
- ChEBI (Chemical Entities of Biological Interest)
- PubChem
- UniProt
- Gene Ontology
- Cyc Knowledge Base
"""

# Chemical reaction templates (5-8 arguments)
CHEMICAL_REACTIONS = [
    # Reaction(type, reactants, products, stoichiometry, conditions, catalyst, yield)
    "Reaction(haber_bosch, [N2,H2], [NH3], [1,3,2], [450C,200atm], Fe, 15%)",
    "Reaction(combustion, [CH4,O2], [CO2,H2O], [1,2,1,2], [25C,1atm], none, 100%)",
    "Reaction(esterification, [CH3COOH,C2H5OH], [CH3COOC2H5,H2O], [1,1,1,1], [reflux,H2SO4], H+, 67%)",
    "Reaction(photosynthesis, [CO2,H2O,light], [C6H12O6,O2], [6,6,energy,1,6], [sunlight,chloroplast], chlorophyll, variable)",
    "Reaction(neutralization, [HCl,NaOH], [NaCl,H2O], [1,1,1,1], [25C,aqueous], none, 100%)",
]

# Molecular structure templates (6-7 arguments)
MOLECULAR_STRUCTURES = [
    # MolecularStructure(compound, formula, geometry, bond_angles, hybridization, dipole, symmetry)
    "MolecularStructure(water, H2O, bent, 104.5deg, sp3, 1.85D, C2v)",
    "MolecularStructure(methane, CH4, tetrahedral, 109.5deg, sp3, 0D, Td)",
    "MolecularStructure(ammonia, NH3, pyramidal, 107deg, sp3, 1.42D, C3v)",
    "MolecularStructure(carbon_dioxide, CO2, linear, 180deg, sp, 0D, D_inf_h)",
    "MolecularStructure(benzene, C6H6, planar, 120deg, sp2, 0D, D6h)",
    "MolecularStructure(sulfur_hexafluoride, SF6, octahedral, 90deg, sp3d2, 0D, Oh)",
]

# Protein interactions (5-6 arguments)
PROTEIN_INTERACTIONS = [
    # ProteinInteraction(protein1, protein2, type, location, affinity, function)
    "ProteinInteraction(insulin, insulin_receptor, binding, cell_membrane, 0.1nM, glucose_uptake)",
    "ProteinInteraction(p53, MDM2, inhibition, nucleus, 100nM, tumor_suppression)",
    "ProteinInteraction(hemoglobin, oxygen, transport, blood, varies_with_pH, oxygen_delivery)",
    "ProteinInteraction(antibody, antigen, recognition, extracellular, 1pM_to_1uM, immune_response)",
    "ProteinInteraction(actin, myosin, mechanical, muscle_fiber, ATP_dependent, contraction)",
]

# Metabolic pathways (6-7 arguments)
METABOLIC_PATHWAYS = [
    # MetabolicPathway(name, substrate, product, enzymes, location, regulation, energy)
    "MetabolicPathway(glycolysis, glucose, pyruvate, [hexokinase,PFK,pyruvate_kinase], cytoplasm, [ATP,citrate], net_2ATP)",
    "MetabolicPathway(krebs_cycle, acetyl_CoA, CO2, [citrate_synthase,isocitrate_dehydrogenase], mitochondria, [NADH,ATP], 3NADH_1FADH2_1GTP)",
    "MetabolicPathway(beta_oxidation, fatty_acid, acetyl_CoA, [acyl_CoA_dehydrogenase], mitochondria, [malonyl_CoA], ATP_yield_varies)",
]

# Crystal structures (7 arguments)
CRYSTAL_STRUCTURES = [
    # CrystalStructure(material, system, a, b, c, space_group, coordination)
    "CrystalStructure(sodium_chloride, cubic, 5.64A, 5.64A, 5.64A, Fm3m, 6)",
    "CrystalStructure(diamond, cubic, 3.57A, 3.57A, 3.57A, Fd3m, 4)",
    "CrystalStructure(graphite, hexagonal, 2.46A, 2.46A, 6.71A, P63/mmc, 3)",
    "CrystalStructure(quartz, hexagonal, 4.91A, 4.91A, 5.40A, P3121, 4)",
]

# Quantum states (6-8 arguments)  
QUANTUM_STATES = [
    # QuantumState(system, n, l, m, spin, energy, wavefunction, probability)
    "QuantumState(hydrogen, 1, 0, 0, +1/2, -13.6eV, 1s, spherical)",
    "QuantumState(hydrogen, 2, 1, 0, +1/2, -3.4eV, 2p, dumbbell)",
    "QuantumState(helium, [1,1], [0,0], [0,0], [+1/2,-1/2], -79eV, 1s2, paired)",
]

# Drug interactions (6-7 arguments)
DRUG_INTERACTIONS = [
    # DrugInteraction(drug1, drug2, effect, mechanism, severity, clinical_action, evidence_level)
    "DrugInteraction(warfarin, aspirin, increased_bleeding, platelet_inhibition, major, avoid_combination, level_A)",
    "DrugInteraction(SSRI, MAOI, serotonin_syndrome, serotonin_accumulation, contraindicated, never_combine, level_A)",
    "DrugInteraction(statins, grapefruit, increased_concentration, CYP3A4_inhibition, moderate, monitor_or_avoid, level_B)",
]

# Gene expression (6-7 arguments)
GENE_EXPRESSION = [
    # GeneExpression(gene, tissue, level, conditions, regulation, function, disease_association)
    "GeneExpression(BRCA1, breast_tissue, high, normal, estrogen_responsive, DNA_repair, breast_cancer)",
    "GeneExpression(insulin, pancreas_beta_cells, variable, glucose_dependent, transcriptional, glucose_homeostasis, diabetes)",
    "GeneExpression(p53, all_tissues, low, normal, stress_induced, tumor_suppression, various_cancers)",
]

# Enzyme kinetics (6 arguments)
ENZYME_KINETICS = [
    # EnzymeKinetics(enzyme, substrate, Km, Vmax, kcat, efficiency)
    "EnzymeKinetics(carbonic_anhydrase, CO2, 12mM, 600000/s, 600000/s, 5e7/M/s)",
    "EnzymeKinetics(catalase, H2O2, 25mM, 40000000/s, 40000000/s, 1.6e9/M/s)",
    "EnzymeKinetics(hexokinase, glucose, 0.05mM, varies, 250/s, 5e6/M/s)",
]

# Physical properties (5-8 arguments)
PHYSICAL_PROPERTIES = [
    # PhysicalProperty(substance, property, value, conditions, phase, measurement_method, uncertainty)
    "PhysicalProperty(water, boiling_point, 100C, 1atm, liquid_to_gas, thermometry, 0.01C)",
    "PhysicalProperty(iron, density, 7.874g/cm3, 20C, solid, displacement, 0.001g/cm3)",
    "PhysicalProperty(ethanol, vapor_pressure, 5.95kPa, 20C, liquid, manometry, 0.05kPa)",
]

def get_scientific_fact_templates():
    """Return all scientific fact templates organized by domain"""
    return {
        'chemistry': CHEMICAL_REACTIONS + MOLECULAR_STRUCTURES,
        'biochemistry': PROTEIN_INTERACTIONS + METABOLIC_PATHWAYS + ENZYME_KINETICS,
        'physics': CRYSTAL_STRUCTURES + QUANTUM_STATES,
        'medicine': DRUG_INTERACTIONS,
        'biology': GENE_EXPRESSION,
        'materials': PHYSICAL_PROPERTIES
    }

def get_template_explanations():
    """Return explanations for each template type"""
    return {
        'Reaction': "Chemical reaction with reactants, products, stoichiometry, conditions, catalyst, yield",
        'MolecularStructure': "3D molecular geometry with bond angles, hybridization, dipole moment, symmetry",
        'ProteinInteraction': "Protein-protein or protein-ligand interactions with affinity and function",
        'MetabolicPathway': "Biochemical pathways with substrates, products, enzymes, regulation",
        'CrystalStructure': "Crystallographic data with lattice parameters and space group",
        'QuantumState': "Quantum mechanical states with quantum numbers and energy levels",
        'DrugInteraction': "Pharmaceutical interactions with clinical significance",
        'GeneExpression': "Gene expression patterns in different tissues/conditions",
        'EnzymeKinetics': "Enzyme kinetic parameters (Km, Vmax, kcat, efficiency)",
        'PhysicalProperty': "Measured physical properties under specific conditions"
    }

# Export for use in fact_extractor
__all__ = ['get_scientific_fact_templates', 'get_template_explanations']
