import z3
from pathlib import Path
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class ConstitutionalViolation(Exception):
    pass

class SMTVerificationTimeout(Exception):
    pass

class MandatorySMTVerifier:
    def __init__(self, project_root: Path = None, timeout: int = 5000):
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.smt_file = self.project_root / 'hak_gal_constitution_v2_2.smt2'
        self.solver = z3.Solver()
        self.solver.set("timeout", timeout)
        
        if not self.smt_file.exists():
            raise FileNotFoundError(f"SMT constraints file not found at {self.smt_file}")
            
        try:
            self.solver.from_file(str(self.smt_file))
        except Exception as e:
            logger.error(f"Failed to load SMT constraints: {e}")
            raise

    def verify_governance_decision(self, decision: Dict, context: Dict) -> Dict:
        self.solver.push() # Create a new scope for this check
        
        try:
            # Declare constants for the decision values
            harm = z3.Real('HarmHumanProb')
            sustain = z3.Real('SustainIndex')
            universal = z3.Bool('Universalizable')
            legal = z3.Bool('ExternallyLegal')

            # Add assertions for the current decision
            self.solver.add(harm == decision['metrics']['harm_prob'])
            self.solver.add(sustain == decision['metrics']['sustain_index'])
            self.solver.add(universal == decision['metrics']['universalizable'])
            self.solver.add(legal == context.get('externally_legal', True))

            result = self.solver.check()

            if result == z3.unsat:
                raise ConstitutionalViolation("Decision violates formal constraints.")
            elif result == z3.unknown:
                raise SMTVerificationTimeout("SMT verification timed out or was inconclusive.")
            
            model = self.solver.model()
            verification_hash = self._compute_verification_hash(decision, model)

            return {
                'satisfiable': True,
                'model': str(model),
                'verification_hash': verification_hash
            }
        finally:
            self.solver.pop() # Clean up the scope

    def _compute_verification_hash(self, decision: Dict, model) -> str:
        import hashlib
        data = f"{decision['decision_id']}:{str(model)}"
        return hashlib.sha256(data.encode()).hexdigest()
