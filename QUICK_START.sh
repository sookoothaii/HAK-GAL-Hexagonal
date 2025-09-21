#!/bin/bash
# QUICK START GUIDE - HAK_GAL Multi-Argument Facts
# ==================================================
# Für die nächste Arbeitsinstanz

echo "=================================="
echo "HAK_GAL KB - Quick Start Guide"
echo "=================================="

# 1. KRITISCH: Backend muss neugestartet werden!
echo ""
echo "⚠️  WICHTIG: Backend neustarten nach Schema-Änderungen!"
echo "   cd src_hexagonal"
echo "   python hexagonal_api_enhanced_clean.py"
echo ""

# 2. Status der Knowledge Base
echo "📊 Aktueller Status (2025-01-10):"
echo "   - 199 Facts in KB"
echo "   - Davon n-äre Facts (3-10 Args): ~50"
echo "   - Q(...) Schema aktiv für Unsicherheiten"
echo ""

# 3. Wichtigste geänderte Dateien
echo "📝 Kritische Dateien:"
echo "   1. fact_extractor_universal.py - Kontextbezogene Fact-Generierung"
echo "   2. quantity_schema.py - Q(value, unit, error) Implementation"
echo "   3. scientific_kb_architecture.py - Multi-Domain Support"
echo ""

# 4. Test-Commands
echo "🧪 Test-Befehle:"
echo "   python test_multi_arg_facts.py    # Test Multi-Arg Generation"
echo "   python quantity_schema.py          # Test Q(...) Schema"
echo "   python setup_chemistry_kb.py      # Test Chemistry KB"
echo ""

# 5. Fact-Formate
echo "📐 Fact-Formate:"
echo ""
echo "Standard n-är (3-10 Argumente):"
echo "  ChemicalReaction(H2, O2, H2O, catalyst:none, 298K, 1atm)"
echo ""
echo "Mit Quantities und Unsicherheiten:"
echo "  ReactionKinetics(name, k:Q(2.3e-4, s^-1, err_rel:5), Ea:Q(75.3, kJ/mol, err_abs:2.1), ...)"
echo ""
echo "Organische Reaktionen mit Yield:"
echo "  OrganicReaction(substrate, reagent, product, SN2, DMSO, T:Q(298, K), yield:Q(92, %, err_abs:2))"
echo ""

# 6. Nächste TODOs
echo "📋 Nächste Schritte:"
echo "   [ ] Frontend anpassen für n-äre Facts Darstellung"
echo "   [ ] Weitere wissenschaftliche Facts einfügen"
echo "   [ ] Validierung implementieren (Stöchiometrie)"
echo "   [ ] SMILES/InChI Integration"
echo ""

# 7. Aufgabenteilung
echo "👥 Aufgabenteilung:"
echo "   Claude: DB-Management, Frontend, Strukturierung"
echo "   GPT-5:  Wissenschaftliche Facts, Validierung"
echo "   Siehe: GPT5_TASKS.md"
echo ""

echo "=================================="
echo "Detaillierte Dokumentation:"
echo "→ PROJECT_SUMMARY_2025-01-10.md"
echo "=================================="
