// MultiArgFactGenerator.tsx
// Enhanced Fact Generator with Multi-Argument Support (3-7 args)
// =================================================================

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Shuffle, Plus, Copy, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

interface FactTemplate {
  predicate: string;
  argCount: number;
  argNames: string[];
  examples: string[][];
  description: string;
  domain: string;
}

// Multi-argument fact templates (3-7 arguments)
const FACT_TEMPLATES: FactTemplate[] = [
  // 3-argument facts
  {
    predicate: "Located",
    argCount: 3,
    argNames: ["entity", "city", "country"],
    examples: [
      ["EiffelTower", "Paris", "France"],
      ["StatueOfLiberty", "NewYork", "USA"],
      ["BigBen", "London", "UK"],
      ["BrandenburgGate", "Berlin", "Germany"],
      ["SydneyOpera", "Sydney", "Australia"]
    ],
    description: "Geographic location with city and country",
    domain: "geography"
  },
  {
    predicate: "ChemicalReaction",
    argCount: 3,
    argNames: ["reactant1", "reactant2", "product"],
    examples: [
      ["H2", "O2", "H2O"],
      ["Na", "Cl", "NaCl"],
      ["Fe", "O2", "Fe2O3"],
      ["C", "O2", "CO2"],
      ["N2", "H2", "NH3"]
    ],
    description: "Chemical reaction with reactants and product",
    domain: "chemistry"
  },
  
  // 4-argument facts
  {
    predicate: "Transfer",
    argCount: 4,
    argNames: ["agent", "object", "from", "to"],
    examples: [
      ["Electron", "Energy", "Orbital1", "Orbital2"],
      ["Bank", "Money", "AccountA", "AccountB"],
      ["Pump", "Water", "Tank1", "Tank2"],
      ["Courier", "Package", "Warehouse", "Customer"],
      ["Network", "Data", "Server1", "Server2"]
    ],
    description: "Transfer of object from source to destination",
    domain: "physics"
  },
  {
    predicate: "AcidBaseReaction",
    argCount: 4,
    argNames: ["acid", "base", "salt", "water"],
    examples: [
      ["HCl", "NaOH", "NaCl", "H2O"],
      ["H2SO4", "KOH", "K2SO4", "H2O"],
      ["HNO3", "Ca(OH)2", "Ca(NO3)2", "H2O"],
      ["CH3COOH", "NaOH", "CH3COONa", "H2O"],
      ["H3PO4", "LiOH", "Li3PO4", "H2O"]
    ],
    description: "Acid-base neutralization reaction",
    domain: "chemistry"
  },
  
  // 5-argument facts
  {
    predicate: "Combustion",
    argCount: 5,
    argNames: ["fuel", "oxidizer", "product1", "product2", "conditions"],
    examples: [
      ["CH4", "O2", "CO2", "H2O", "temperature:298K"],
      ["C2H6", "O2", "CO2", "H2O", "pressure:1atm"],
      ["C3H8", "O2", "CO2", "H2O", "catalyst:Pt"],
      ["C8H18", "O2", "CO2", "H2O", "spark:required"],
      ["H2", "O2", "H2O", "none", "temperature:500K"]
    ],
    description: "Combustion reaction with conditions",
    domain: "chemistry"
  },
  {
    predicate: "BiologicalProcess",
    argCount: 5,
    argNames: ["organism", "process", "substrate", "product", "location"],
    examples: [
      ["Bacteria", "Fermentation", "Glucose", "Ethanol", "Cytoplasm"],
      ["Plant", "Photosynthesis", "CO2", "Glucose", "Chloroplast"],
      ["Human", "Respiration", "Glucose", "ATP", "Mitochondria"],
      ["Yeast", "Glycolysis", "Glucose", "Pyruvate", "Cytoplasm"],
      ["Liver", "Gluconeogenesis", "Pyruvate", "Glucose", "Hepatocyte"]
    ],
    description: "Biological process with location",
    domain: "biology"
  },
  
  // 6-argument facts
  {
    predicate: "MolecularGeometry",
    argCount: 6,
    argNames: ["molecule", "central_atom", "ligand", "shape", "hybridization", "angle"],
    examples: [
      ["CH4", "carbon", "hydrogen", "tetrahedral", "sp3", "angle:109.5deg"],
      ["NH3", "nitrogen", "hydrogen", "pyramidal", "sp3", "angle:107deg"],
      ["H2O", "oxygen", "hydrogen", "bent", "sp3", "angle:104.5deg"],
      ["BF3", "boron", "fluorine", "planar", "sp2", "angle:120deg"],
      ["SF6", "sulfur", "fluorine", "octahedral", "sp3d2", "angle:90deg"]
    ],
    description: "Molecular structure and geometry",
    domain: "chemistry"
  },
  {
    predicate: "ElectronicTransition",
    argCount: 6,
    argNames: ["atom", "initial_state", "final_state", "energy", "wavelength", "type"],
    examples: [
      ["Hydrogen", "n2", "n1", "10.2eV", "121.6nm", "Lyman"],
      ["Helium", "2s", "1s", "20.6eV", "60.1nm", "UV"],
      ["Sodium", "3p", "3s", "2.1eV", "589nm", "D-line"],
      ["Mercury", "6p", "6s", "4.9eV", "253.7nm", "UV"],
      ["Neon", "3p", "3s", "1.96eV", "632.8nm", "Laser"]
    ],
    description: "Electronic transitions in atoms",
    domain: "physics"
  },
  
  // 7-argument facts
  {
    predicate: "Motion",
    argCount: 7,
    argNames: ["type", "object", "value", "initial", "final", "condition", "framework"],
    examples: [
      ["escape_velocity", "earth", "11.2km_s", "gravitational_potential", "threshold", "no_return", "classical"],
      ["orbital_velocity", "ISS", "7.66km_s", "circular_orbit", "400km_altitude", "stable", "newtonian"],
      ["terminal_velocity", "raindrop", "9m_s", "free_fall", "equilibrium", "air_resistance", "fluid_dynamics"],
      ["relativistic", "electron", "0.9c", "rest_mass", "lorentz_factor", "accelerator", "special_relativity"],
      ["quantum_tunneling", "alpha_particle", "5MeV", "nuclear_barrier", "escape", "probability:0.01", "quantum"]
    ],
    description: "Complex motion with multiple parameters",
    domain: "physics"
  },
  {
    predicate: "ChemicalEquilibrium",
    argCount: 7,
    argNames: ["reaction", "reactant1", "reactant2", "product1", "product2", "Keq", "conditions"],
    examples: [
      ["Haber", "N2", "H2", "NH3", "heat", "Keq:0.5", "T:450C_P:200atm"],
      ["Water", "H2O", "H+", "OH-", "none", "Kw:1e-14", "T:25C"],
      ["Esterification", "RCOOH", "ROH", "RCOOR", "H2O", "Keq:4.0", "catalyst:H2SO4"],
      ["Dimerization", "NO2", "none", "N2O4", "none", "Keq:8.7", "T:298K"],
      ["Dissociation", "PCl5", "none", "PCl3", "Cl2", "Keq:0.04", "T:523K"]
    ],
    description: "Chemical equilibrium with all parameters",
    domain: "chemistry"
  }
];

export function MultiArgFactGenerator() {
  const [selectedTemplate, setSelectedTemplate] = useState<FactTemplate>(FACT_TEMPLATES[5]); // Start with 6-arg
  const [currentArgs, setCurrentArgs] = useState<string[]>([]);
  const [generatedFacts, setGeneratedFacts] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [stats, setStats] = useState({ total: 0, byComplexity: {} as Record<number, number> });

  // Initialize with random example
  React.useEffect(() => {
    randomizeExample();
  }, [selectedTemplate]);

  const randomizeExample = () => {
    const randomExample = selectedTemplate.examples[
      Math.floor(Math.random() * selectedTemplate.examples.length)
    ];
    setCurrentArgs(randomExample);
  };

  const generateFact = () => {
    if (currentArgs.length !== selectedTemplate.argCount) {
      toast.error(`Need exactly ${selectedTemplate.argCount} arguments`);
      return;
    }

    const fact = `${selectedTemplate.predicate}(${currentArgs.join(', ')}).`;
    setGeneratedFacts([fact, ...generatedFacts.slice(0, 9)]); // Keep last 10
    return fact;
  };

  const addFactToKB = async () => {
    setIsGenerating(true);
    const fact = generateFact();
    
    if (!fact) {
      setIsGenerating(false);
      return;
    }

    try {
      const response = await fetch('/api/facts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': '515f57956e7bd15ddc3817573598f190'
        },
        body: JSON.stringify({
          statement: fact,
          context: {
            source: 'MultiArgFactGenerator',
            predicate: selectedTemplate.predicate,
            argCount: selectedTemplate.argCount,
            domain: selectedTemplate.domain,
            confidence: 0.95
          }
        })
      });

      if (response.ok) {
        toast.success(`✅ Added ${selectedTemplate.argCount}-argument fact!`);
        
        // Update stats
        setStats(prev => ({
          total: prev.total + 1,
          byComplexity: {
            ...prev.byComplexity,
            [selectedTemplate.argCount]: (prev.byComplexity[selectedTemplate.argCount] || 0) + 1
          }
        }));
        
        randomizeExample(); // Get new example
      } else if (response.status === 409) {
        toast.warning('Fact already exists');
        randomizeExample();
      } else {
        const error = await response.json();
        toast.error(error.message || 'Failed to add fact');
      }
    } catch (error) {
      toast.error('Network error - is backend running on port 5002?');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleArgChange = (index: number, value: string) => {
    const newArgs = [...currentArgs];
    newArgs[index] = value;
    setCurrentArgs(newArgs);
  };

  const copyFact = (fact: string) => {
    navigator.clipboard.writeText(fact);
    toast.success('Copied to clipboard!');
  };

  const getComplexityColor = (argCount: number) => {
    if (argCount <= 3) return 'text-green-500';
    if (argCount <= 5) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <Card className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-bold">Multi-Argument Fact Generator</h2>
        </div>
        <div className="text-right">
          <span className={`text-2xl font-bold ${getComplexityColor(selectedTemplate.argCount)}`}>
            {selectedTemplate.argCount} args
          </span>
          <div className="text-xs text-muted-foreground">
            Total generated: {stats.total}
          </div>
        </div>
      </div>

      {/* Template Selector */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Select Template:</label>
        <select 
          className="w-full p-2 border rounded-md bg-background"
          value={`${selectedTemplate.predicate}_${selectedTemplate.argCount}`}
          onChange={(e) => {
            const [pred, count] = e.target.value.split('_');
            const template = FACT_TEMPLATES.find(
              t => t.predicate === pred && t.argCount === parseInt(count)
            );
            if (template) setSelectedTemplate(template);
          }}
        >
          {FACT_TEMPLATES.map((template) => (
            <option 
              key={`${template.predicate}_${template.argCount}`} 
              value={`${template.predicate}_${template.argCount}`}
            >
              {template.predicate} ({template.argCount} args) - {template.description}
            </option>
          ))}
        </select>
      </div>

      {/* Argument Inputs */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium">Arguments:</label>
          <Button 
            size="sm" 
            variant="outline" 
            onClick={randomizeExample}
          >
            <Shuffle className="w-4 h-4 mr-1" />
            Random Example
          </Button>
        </div>
        
        <div className="grid grid-cols-1 gap-2">
          {selectedTemplate.argNames.map((argName, index) => (
            <div key={index} className="space-y-1">
              <label className="text-xs text-muted-foreground">
                {index + 1}. {argName}
              </label>
              <input
                type="text"
                className="w-full p-2 border rounded-md bg-background"
                placeholder={`Enter ${argName}...`}
                value={currentArgs[index] || ''}
                onChange={(e) => handleArgChange(index, e.target.value)}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Preview */}
      <div className="p-3 bg-secondary/50 rounded-md">
        <div className="text-xs text-muted-foreground mb-1">Preview:</div>
        <div className="font-mono text-sm">
          {selectedTemplate.predicate}({currentArgs.join(', ') || '...'}).
        </div>
      </div>

      {/* Action Buttons */}
      <Button 
        onClick={addFactToKB} 
        disabled={isGenerating || currentArgs.length !== selectedTemplate.argCount}
        className="w-full"
        size="lg"
      >
        <Plus className="w-4 h-4 mr-2" />
        Add {selectedTemplate.argCount}-Argument Fact to Knowledge Base
      </Button>

      {/* Generated Facts History */}
      {generatedFacts.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium">Recent Facts:</h3>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {generatedFacts.map((fact, index) => (
              <div 
                key={index} 
                className="flex items-center justify-between p-2 bg-secondary/30 rounded text-xs"
              >
                <code className="truncate flex-1">{fact}</code>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => copyFact(fact)}
                  className="ml-2"
                >
                  <Copy className="w-3 h-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="pt-2 border-t">
        <div className="text-xs text-muted-foreground space-y-1">
          <p>Domain: <span className="font-medium">{selectedTemplate.domain}</span></p>
          <p>Complexity distribution:</p>
          <div className="flex gap-4 mt-1">
            {[3, 4, 5, 6, 7].map(n => (
              <span key={n} className={getComplexityColor(n)}>
                {n}: {stats.byComplexity[n] || 0}
              </span>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}

export default MultiArgFactGenerator;
