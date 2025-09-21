# Aufgaben für GPT-5/Max - Wissenschaftliche Knowledge Base

## 🎯 Ihre Hauptaufgaben (Wissenschaftliche Expertise)

### 1. FACT GENERATION (Höchste Priorität)
Generieren Sie wissenschaftlich korrekte n-äre Facts (3-10 Argumente) für folgende Bereiche:

#### Template:
```
Predicate(arg1, arg2, arg3, ..., argN).
```

#### Beispiel-Anfragen:

**PHYSIK - Quantenmechanik:**
```
Input: "Quantum Tunneling"
Output:
QuantumTunneling(particle, barrier_height_eV, barrier_width_nm, transmission_probability, wave_function, energy_eV).
TunnelEffect(electron, 5.0eV, 1.0nm, 0.01, psi_function, 4.5eV).
```

**BIOLOGIE - CRISPR:**
```
Input: "CRISPR-Cas9 System"
Output:
CRISPRMechanism(Cas9_enzyme, guide_RNA, PAM_sequence, target_DNA, DSB_position, NHEJ_repair, HDR_template, efficiency_percent).
GeneEditing(SpCas9, sgRNA_ACTG, NGG, BRCA1_exon11, position_1234, NHEJ, donor_DNA, 85_percent).
```

**NEUROWISSENSCHAFT - Gedächtnisbildung:**
```
Input: "Memory Formation"
Output:
MemoryFormation(stimulus, sensory_cortex, hippocampus_CA1, hippocampus_CA3, consolidation_time_hours, protein_synthesis, LTP_strength, storage_cortex).
SynapticPlasticity(glutamate, NMDA_receptor, Ca2+_influx, CaMKII, CREB, gene_transcription, spine_growth, LTP).
```

### 2. WISSENSCHAFTLICHE VALIDIERUNG

Prüfen Sie generierte Facts auf:
- Faktische Korrektheit (Stand 2024/2025)
- Vollständigkeit der Argumente
- Konsistenz mit aktueller Literatur

**Beispiel:**
```
Input: "ProteinSynthesis(ribosome, mRNA, protein)."
Output: "UNVOLLSTÄNDIG. Korrekt wäre:
ProteinSynthesis(ribosome_40S, ribosome_60S, mRNA, tRNA, amino_acids, GTP, elongation_factors, protein, 5_AA_per_second)."
```

### 3. CROSS-DOMAIN CONNECTIONS

Verbinden Sie Facts aus verschiedenen Domänen:

```
Physics: PhotonEnergy(650nm, 3.06e-19J, red_light).
Biology: Photosynthesis(chlorophyll_a, 650nm, P680, electron_excitation).
Connection: PhotoBiologicalProcess(photon_650nm, chlorophyll_P680, excitation, electron_transport, ATP_synthesis).
```

### 4. FACT EXPANSION

Erweitern Sie simple 2-Argument Facts zu wissenschaftlich vollständigen n-ären Facts:

```
Simple: IsA(DNA, Molecule).
Expanded: DNAStructure(DNA, double_helix, nucleotides_ATCG, sugar_phosphate_backbone, antiparallel, major_groove_22A, minor_groove_12A, B_form, 3.4nm_pitch).
```

## 📊 Erwartete Outputs

### Format-Anforderungen:
- **Mindestens 3, maximal 10 Argumente**
- **Einheiten immer angeben** (nm, eV, kDa, mol/L, etc.)
- **Spezifische Werte statt Platzhalter**
- **Aktuelle wissenschaftliche Nomenklatur**

### Qualitätskriterien:
- ✅ Peer-reviewed Literatur als Basis
- ✅ Quantitative Angaben wo möglich
- ✅ Mechanistische Details inkludiert
- ✅ Kontext und Bedingungen spezifiziert

## 🔄 Workflow mit Claude

1. **Sie (GPT-5)**: Generieren wissenschaftliche Facts
2. **Claude**: Strukturiert und speichert in Datenbank
3. **Sie**: Validieren bei Unsicherheiten
4. **Claude**: Implementiert Frontend-Darstellung
5. **Gemeinsam**: Iterative Verbesserung

## 📝 Konkrete erste Aufgabe:

Generieren Sie je 5 n-äre Facts (5-8 Argumente) für:

1. **Photosynthese** (Light & Dark Reactions)
2. **Neuronale Signalübertragung** 
3. **Quantenverschränkung**
4. **Proteinbiosynthese**
5. **Immunantwort** (T-Zell Aktivierung)

Format: 
```
DomainProcess(specific_arg1, value_with_unit, specific_molecule, etc...).
```

---
*Ihre wissenschaftliche Expertise ist essentiell für die Qualität dieser Knowledge Base!*
