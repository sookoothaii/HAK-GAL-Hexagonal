
import re
from typing import Tuple

# Annahme: Die Engines können aus der bestehenden Architektur importiert werden.
# Die exakten Pfade können je nach Projektstruktur angepasst werden.
try:
    from ..infrastructure.engines.aethelred_engine import AethelredEngine
    from ..infrastructure.engines.thesis_engine import ThesisEngine
except (ImportError, ValueError):
    # Fallback für den Fall, dass das Skript standalone analysiert wird
    print("Warnung: Aethelred- und Thesis-Engines konnten nicht importiert werden. Semantische Prüfung ist deaktiviert.")
    class AethelredEngine:
        def check_consistency(self, statement: str) -> Tuple[bool, str]:
            return True, "SKIPPED"
    class ThesisEngine:
        def check_relevance(self, statement: str) -> Tuple[bool, str]:
            return True, "SKIPPED"

class PreValidationEngine:
    """Führt eine Kaskade von Validierungs-Prüfungen für neue Fakten durch."""

    def __init__(self):
        """Initialisiert die benötigten Sub-Engines."""
        self.aethelred = AethelredEngine()
        self.thesis = ThesisEngine()
        # Regex zur Validierung des Formats: Predicate(Entity1,Entity2).
        self.syntactic_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\([^,]+,\s*[^\)]+\)\.")

    def validate(self, statement: str) -> Tuple[bool, str]:
        """
        Führt alle Validierungs-Schritte aus.
        
        Returns:
            Ein Tupel (bool, str), wobei bool angibt, ob die Validierung erfolgreich war,
            und str eine Erfolgs- oder Fehlermeldung enthält.
        """
        
        # 1. Syntaktische Prüfung
        is_syntactically_valid, syntactic_message = self._check_syntax(statement)
        if not is_syntactically_valid:
            return False, syntactic_message

        # 2. Semantische Konsistenzprüfung (Aethelred)
        is_consistent, consistency_message = self.aethelred.check_consistency(statement)
        if not is_consistent:
            return False, f"Aethelred Consistency Check failed: {consistency_message}"

        # 3. Semantische Relevanzprüfung (Thesis)
        is_relevant, relevance_message = self.thesis.check_relevance(statement)
        if not is_relevant:
            return False, f"Thesis Relevance Check failed: {relevance_message}"

        return True, "Validation OK"

    def _check_syntax(self, statement: str) -> Tuple[bool, str]:
        """Prüft, ob der Fakt dem erwarteten Format Predicate(Entity1,Entity2). entspricht."""
        if not isinstance(statement, str):
            return False, "Statement is not a string."
        
        if not statement.endswith('.'):
            return False, "Statement must end with a period."

        if not self.syntactic_pattern.match(statement):
            return False, "Invalid format. Expected Predicate(Entity1,Entity2)."
        
        return True, "Syntax OK"

# --- Integrations-Anleitung ---
#
# Um diesen Validator zu nutzen, muss die `add_fact`-Methode im API-Endpunkt
# (vermutlich in `hexagonal_api_enhanced_clean.py`) wie folgt angepasst werden:
#
# 1. Importieren Sie die neue Engine:
#    from infrastructure.pre_validation_engine import PreValidationEngine
#
# 2. Initialisieren Sie die Engine im Konstruktor der `HexagonalAPI`-Klasse:
#    self.pre_validator = PreValidationEngine()
#
# 3. Rufen Sie die `validate`-Methode am Anfang der `add_fact`-Funktion auf:
#
#    @self.app.route('/api/facts', methods=['POST'])
#    def add_fact():
#        data = request.get_json(silent=True) or {}
#        statement = (data.get('statement') or ...).strip()
#
#        # >>> START: Integration des Pre-Validators <<<
#        is_valid, message = self.pre_validator.validate(statement)
#        if not is_valid:
#            return jsonify({'error': f'Pre-validation failed: {message}'}), 400
#        # >>> END: Integration des Pre-Validators <<<
#
#        # ... restlicher Code der add_fact-Funktion ...
#
