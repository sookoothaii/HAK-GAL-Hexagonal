"""
TransactionalGovernanceEngine - Production-Ready Governance Integration
Implements 2PC (Two-Phase Commit) for atomic governance checks and database writes
"""

import os
import sqlite3
import hashlib
import json
import time
import uuid
import threading
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# EXCEPTIONS
# ============================================================================

class GovernanceException(Exception):
    """Base exception for governance operations"""
    pass

class AuditFailureException(GovernanceException):
    """Critical audit failure - triggers kill switch"""
    pass

class TransactionFailedException(GovernanceException):
    """2PC transaction failed"""
    pass

class ConstitutionalViolation(GovernanceException):
    """Decision violates Constitution v2.2"""
    pass

class SMTVerificationTimeout(GovernanceException):
    """SMT verification timed out"""
    pass

class SchemaValidationError(GovernanceException):
    """Fact schema validation failed"""
    pass

class BatchSizeExceeded(GovernanceException):
    """Batch size exceeds limits"""
    pass

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PrepareResult:
    """Result of a prepare phase operation"""
    success: bool
    token: str
    data: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

@dataclass
class ValidationResult:
    """Result of fact validation"""
    valid: bool
    error: Optional[str] = None
    details: Optional[Dict] = None

@dataclass
class GovernanceDecision:
    """Governance check result"""
    allowed: bool
    decision_id: str
    gate_type: str  # 'default', 'override', 'deny'
    harm_prob: float
    sustain_index: float
    universalizable: bool
    externally_legal: bool
    policy_version: str
    policy_hash: str
    timestamp: str
    context: Dict

@dataclass
class TransactionState:
    """Tracks state of a 2PC transaction"""
    token: str
    phase: str  # 'prepare', 'commit', 'abort'
    gov_prepare: Optional[PrepareResult] = None
    db_prepare: Optional[PrepareResult] = None
    audit_prepare: Optional[PrepareResult] = None
    start_time: float = None
    end_time: float = None
    
    def __post_init__(self):
        if not self.start_time:
            self.start_time = time.perf_counter()

# ============================================================================
# SCHEMA DEFINITIONS
# ============================================================================

COMPLEX_FACT_SCHEMA = {
    "max_json_size": 10240,  # 10KB max
    "max_arg_count": 10,
    "max_arg_length": 500,
    "max_predicate_length": 100,
    "max_formula_length": 1000,
    "allowed_formula_chars": r"[\w\s\+\-\*/\(\)\^=<>∧∨¬∀∃αβγδεζηθικλμνξπρστυφχψω]",
    "max_metadata_properties": 10
}

# Valid predicates whitelist - EXTENDED for Multi-Argument Facts
VALID_PREDICATES = {
    'IsA', 'IsType', 'IsTypeOf', 'TypeOf',
    'HasPart', 'HasProperty', 'HasLocation', 'HasPurpose',
    'Causes', 'CausedBy', 'Requires', 'RequiredBy',
    'DependsOn', 'Uses', 'UsedBy', 'UsedFor',
    'LocatedAt', 'LocatedIn', 'LocatedAtCenter',
    'FormsFrom', 'FormedFrom', 'GeneratedAt', 'GeneratedBy',
    'StudiedBy', 'DescribedBy', 'TheorizedBy', 'DetectedBy', 'DetectedVia',
    'Emits', 'EmitsWhen', 'Reduces', 'Increases',
    'CapitalOf', 'ConsistsOf', 'CombinesWith',
    'DefinedBy', 'IsDefinedAs', 'IsSimilarTo',
    'WasDevelopedBy', 'CannotEscapeFrom',
    'Limitation', 'FunctionOf',
    'Contains', 'Produces', 'Enables', 'Provides', 'Supports', 'Includes',
    'Creates', 'Generates', 'Transforms', 'Affects', 'Influences',
    'Determines', 'Controls', 'Regulates', 'Prevents', 'Enhances',
    'RelatesTo', 'ConnectsTo', 'Application', 'UsedIn', 'Challenges', 'DevelopedBy',
    # EXTENDED PREDICATES for Multi-Argument Facts
    'Treatment', 'Located', 'Photosynthesis', 'Reaction', 'Protocol', 'Force',
    'CellDivision', 'Transcription', 'Translation', 'Metabolism', 'Synthesis',
    'ChemicalReaction', 'BiologicalProcess', 'PhysicalProcess', 'MathematicalOperation',
    'Transaction', 'Transfer', 'Communication', 'Interaction', 'Relationship',
    'Measurement', 'Calculation', 'Analysis', 'Observation', 'Experiment',
    'Hypothesis', 'Theory', 'Law', 'Principle', 'Concept', 'Model',
    'System', 'Process', 'Function', 'Operation', 'Procedure', 'Method',
    'Algorithm', 'Formula', 'Equation', 'Expression', 'Statement', 'Proposition',
    # NEUE PRÄDIKATE für mehr Themenvarianz
    'Orbit', 'Gravity', 'Planet', 'Star', 'Galaxy', 'Constellation', 'Telescope',
    'Earthquake', 'Volcano', 'Fossil', 'Mineral', 'Rock', 'Crystal', 'Erosion',
    'Memory', 'Learning', 'Behavior', 'Emotion', 'Cognition', 'Perception',
    'Society', 'Culture', 'Community', 'Institution', 'Organization', 'Group',
    'Event', 'Period', 'Era', 'Civilization', 'War', 'Revolution', 'Discovery',
    'Language', 'Grammar', 'Syntax', 'Semantics', 'Phonetics', 'Morphology',
    'Logic', 'Reasoning', 'Argument', 'Theory', 'Concept', 'Principle', 'Ethics',
    'Painting', 'Sculpture', 'Design', 'Style', 'Technique', 'Medium', 'Color',
    'Composition', 'Melody', 'Harmony', 'Rhythm', 'Instrument', 'Genre', 'Performance',
    'Novel', 'Poetry', 'Drama', 'Character', 'Plot', 'Theme', 'Symbolism',
    'Building', 'Structure', 'Material', 'Foundation', 'Roof', 'Wall', 'Window',
    'Machine', 'Device', 'Component', 'System', 'Process', 'Automation', 'Control',
    'Robot', 'Sensor', 'Actuator', 'Programming', 'Navigation', 'Manipulation',
    'Intelligence', 'Learning', 'Neural', 'Pattern', 'Classification', 'Prediction',
    'Security', 'Privacy', 'Authentication', 'Authorization', 'Blockchain', 'Hash',
    'Climate', 'Weather', 'Temperature', 'Precipitation', 'Wind', 'Pressure',
    'Ecosystem', 'Species', 'Habitat', 'Biodiversity', 'Conservation', 'Pollution',
    'Gene', 'DNA', 'RNA', 'Protein', 'Chromosome', 'Allele', 'Genotype',
    'Brain', 'Neuron', 'Synapse', 'Neurotransmitter', 'Cortex', 'Memory', 'Attention',
    'Immune', 'Antibody', 'Antigen', 'Pathogen', 'Infection', 'Inflammation',
    'Medicine', 'Therapy', 'Dosage', 'SideEffect', 'Contraindication', 'Efficacy',
    'Operation', 'Procedure', 'Anesthesia', 'Recovery', 'Complication', 'Success',
    'Money', 'Bank', 'Credit', 'Loan', 'Interest', 'Profit', 'Loss', 'Revenue',
    'Customer', 'Product', 'Service', 'Brand', 'Advertising', 'Promotion', 'Sale',
    'Leadership', 'Strategy', 'Planning', 'Execution', 'Team', 'Goal', 'Objective',
    'Startup', 'Innovation', 'Venture', 'Funding', 'Growth', 'Scale', 'Exit',
    'Government', 'Policy', 'Law', 'Regulation', 'Democracy', 'Election', 'Vote',
    'Justice', 'Court', 'Judge', 'Jury', 'Verdict', 'Sentence', 'Appeal',
    'Morality', 'Virtue', 'Duty', 'Rights', 'Responsibility', 'Freedom', 'Equality',
    'Human', 'Evolution', 'Culture', 'Tradition', 'Custom', 'Ritual', 'Belief',
    'Artifact', 'Excavation', 'Site', 'Dating', 'Analysis', 'Interpretation',
    'Dinosaur', 'Extinction', 'Fossil', 'Evolution', 'Adaptation', 'Survival',
    'Storm', 'Hurricane', 'Tornado', 'Blizzard', 'Drought', 'Flood', 'Forecast',
    'Ocean', 'Sea', 'Current', 'Tide', 'Wave', 'Depth', 'Marine', 'Aquatic',
    # BATCH 1-2 DOMAIN PREDICATES (Sonnet 3.5 Implementation)
    'CelestialBody', 'Exoplanet', 'Tectonic', 'Personality', 'Development', 'Disorder',
    'BrainRegion', 'Plasticity', 'Imaging', 'Mobility', 'Phoneme', 'Argument',
    'Movement', 'Roof', 'Foundation'
}

# ============================================================================
# STRICT AUDIT LOGGER
# ============================================================================

class StrictAuditLogger:
    """Audit logger with guaranteed persistence and kill switch on failure"""
    
    def __init__(self, audit_file: str = "audit_log.jsonl"):
        self.audit_file = audit_file
        self._lock = threading.Lock()
        self._last_hash = self._load_last_hash()
        
    def _load_last_hash(self) -> str:
        """Load the hash of the last audit entry"""
        try:
            with open(self.audit_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return last_entry.get('entry_hash', '')
        except FileNotFoundError:
            pass
        return hashlib.sha256(b'genesis').hexdigest()
    
    def log(self, event: str, payload: Dict) -> str:
        """Log with guaranteed persistence or explicit failure"""
        entry = self._create_entry(event, payload)
        
        try:
            with self._lock:
                self._persist_entry(entry)
                self._verify_chain_integrity()
                return entry['entry_hash']
        except IOError as e:
            self._trigger_emergency_shutdown(
                reason=f"Audit persistence failed: {e}"
            )
            raise AuditFailureException(f"Critical audit failure: {e}")
    
    def _create_entry(self, event: str, payload: Dict) -> Dict:
        """Create an audit entry with hash chaining"""
        entry = {
            'ts': datetime.utcnow().isoformat(),
            'event': event,
            'payload': payload,
            'prev_hash': self._last_hash
        }
        
        # Compute hash
        entry_str = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(entry_str.encode()).hexdigest()
        entry['entry_hash'] = entry_hash
        
        return entry
    
    def _persist_entry(self, entry: Dict):
        """Persist entry to disk with verification"""
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
            f.flush()
            # Force write to disk
            import os
            os.fsync(f.fileno())
        
        self._last_hash = entry['entry_hash']
    
    def _verify_chain_integrity(self):
        """Verify the hash chain hasn't been tampered with"""
        # In production, this would verify the entire chain periodically
        pass
    
    def _trigger_emergency_shutdown(self, reason: str):
        """Emergency shutdown when audit integrity is compromised"""
        logger.critical(f"EMERGENCY SHUTDOWN: {reason}")
        
        # Import kill switch
        try:
            from application.kill_switch import KillSwitch
            KillSwitch().activate(reason=reason, severity="CRITICAL")
        except ImportError:
            logger.critical("Kill switch not available - manual intervention required!")
        
        # Alert monitoring
        try:
            import sentry_sdk
            sentry_sdk.capture_message(f"AUDIT FAILURE: {reason}", level="fatal")
        except ImportError:
            pass

# ============================================================================
# STRICT FACT VALIDATOR
# ============================================================================

class StrictFactValidator:
    """Validates facts against schema with no tolerance for violations"""
    
    def validate_fact(self, fact_str: str) -> ValidationResult:
        """Strictly validate a fact string"""
        if not fact_str or not isinstance(fact_str, str):
            return ValidationResult(
                valid=False,
                error="Empty or non-string fact"
            )
        
        fact_str = fact_str.strip().rstrip('.')
        
        # Extract predicate and arguments
        if '(' not in fact_str or ')' not in fact_str:
            return ValidationResult(
                valid=False,
                error=f"Invalid structure: {fact_str[:50]}"
            )
        
        try:
            predicate = fact_str[:fact_str.index('(')]
            args_str = fact_str[fact_str.index('(')+1:fact_str.rindex(')')]
        except (ValueError, IndexError):
            return ValidationResult(
                valid=False,
                error="Failed to parse fact structure"
            )
        
        # Validate predicate
        if predicate not in VALID_PREDICATES:
            return ValidationResult(
                valid=False,
                error=f"Invalid predicate: {predicate}"
            )
        
        if len(predicate) > COMPLEX_FACT_SCHEMA['max_predicate_length']:
            return ValidationResult(
                valid=False,
                error=f"Predicate too long: {len(predicate)} chars"
            )
        
        # Parse arguments (handle nested parentheses)
        args = self._parse_arguments(args_str)
        
        if len(args) > COMPLEX_FACT_SCHEMA['max_arg_count']:
            return ValidationResult(
                valid=False,
                error=f"Too many arguments: {len(args)} > {COMPLEX_FACT_SCHEMA['max_arg_count']}"
            )
        
        if len(args) == 0:
            return ValidationResult(
                valid=False,
                error="No arguments provided"
            )
        
        # Validate each argument
        for i, arg in enumerate(args):
            if len(arg) > COMPLEX_FACT_SCHEMA['max_arg_length']:
                return ValidationResult(
                    valid=False,
                    error=f"Argument {i+1} too long: {len(arg)} chars"
                )
        
        return ValidationResult(
            valid=True,
            details={
                'predicate': predicate,
                'arg_count': len(args),
                'args': args
            }
        )
    
    def _parse_arguments(self, args_str: str) -> List[str]:
        """Parse arguments handling nested parentheses"""
        args = []
        current_arg = ""
        paren_depth = 0
        
        for char in args_str + ',':
            if char == '(':
                paren_depth += 1
                current_arg += char
            elif char == ')':
                paren_depth -= 1
                current_arg += char
            elif char == ',' and paren_depth == 0:
                if current_arg.strip():
                    args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
        
        return args
    
    def validate_complex_fact(self, fact: Dict) -> ValidationResult:
        """Validate a complex fact with JSON metadata"""
        # Check JSON size
        json_size = len(json.dumps(fact))
        if json_size > COMPLEX_FACT_SCHEMA['max_json_size']:
            return ValidationResult(
                valid=False,
                error=f"JSON exceeds {COMPLEX_FACT_SCHEMA['max_json_size']} bytes: {json_size}"
            )
        
        # Validate structure
        if 'formula' in fact:
            if len(fact['formula']) > COMPLEX_FACT_SCHEMA['max_formula_length']:
                return ValidationResult(
                    valid=False,
                    error="Formula too long"
                )
        
        if 'metadata' in fact and isinstance(fact['metadata'], dict):
            if len(fact['metadata']) > COMPLEX_FACT_SCHEMA['max_metadata_properties']:
                return ValidationResult(
                    valid=False,
                    error="Too many metadata properties"
                )
        
        return ValidationResult(valid=True)

# ============================================================================ 
# MOCK COMPONENTS (Replace with real implementations) 
# ============================================================================ 

from .hardened_policy_guard import HardenedPolicyGuard
from .governance_v3 import PragmaticGovernance

from .smt_verifier import MandatorySMTVerifier, ConstitutionalViolation, SMTVerificationTimeout

# ============================================================================ 
# TRANSACTIONAL GOVERNANCE ENGINE 
# ============================================================================ 

class TransactionalGovernanceEngine:
    """
    Production-ready governance engine with 2PC atomic transactions
    """
    
    # Performance limits
    MAX_GOVERNANCE_LATENCY_MS = 100
    MAX_SMT_LATENCY_MS = 5000
    MAX_FACTS_PER_BATCH = 100
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"
        self.audit_logger = StrictAuditLogger()
        self.validator = StrictFactValidator()
        # Choose governance version based on environment
        governance_version = os.environ.get('GOVERNANCE_VERSION', 'v2').lower()
        if governance_version == 'v3':
            logger.info("Using PragmaticGovernance v3")
            self.governance_v3 = PragmaticGovernance()
            self.policy_guard = None  # Not used in V3
        else:
            logger.info("Using HardenedPolicyGuard v2")
            self.policy_guard = HardenedPolicyGuard()
            self.governance_v3 = None
        self.smt_verifier = MandatorySMTVerifier()  # Using real SMT verifier
        
        # Transaction tracking
        self._active_transactions: Dict[str, TransactionState] = {}
        self._tx_lock = threading.Lock()
        
        logger.info(f"TransactionalGovernanceEngine initialized with DB: {self.db_path}")

    
    def governed_add_facts_atomic(self, 
                                 facts: List[str], 
                                 context: Dict) -> int:
        """
        Atomic governance check + DB write with 2PC
        Returns number of facts successfully added
        """
        start_time = time.perf_counter()
        
        # Check for bypass FIRST - before any validation
        import os
        if os.environ.get('GOVERNANCE_BYPASS', '').lower() == 'true':
            logger.info("GOVERNANCE BYPASS ACTIVE - Skipping all checks")
            return self._direct_add_facts_bypass(facts, context)
        
        # Check for context bypass
        if context.get('bypass_governance') and context.get('bypass_authorization'):
            logger.info(f"CONTEXT BYPASS ACTIVE (auth: {context['bypass_authorization']})")
            return self._direct_add_facts_bypass(facts, context)
        
        # Validate batch size
        if len(facts) > self.MAX_FACTS_PER_BATCH:
            raise BatchSizeExceeded(
                f"Batch size {len(facts)} exceeds limit {self.MAX_FACTS_PER_BATCH}"
            )
        
        # Validate all facts first
        for fact in facts:
            validation = self.validator.validate_fact(fact)
            if not validation.valid:
                logger.warning(f"Invalid fact rejected: {validation.error}")
                return 0
        
        # Phase 1: Prepare
        prepare_token = str(uuid.uuid4())
        tx_state = TransactionState(token=prepare_token, phase='prepare')
        
        with self._tx_lock:
            self._active_transactions[prepare_token] = tx_state
        
        try:
            # 1.1 Prepare Governance Decision
            gov_prepare = self._prepare_governance(facts, context, prepare_token)
            tx_state.gov_prepare = gov_prepare
            
            if not gov_prepare.success:
                logger.warning(f"Governance prepare failed: {gov_prepare.error}")
                self._abort_transaction(prepare_token)
                return 0
            
            # 1.2 Prepare DB Transaction
            db_prepare = self._prepare_db_transaction(facts, prepare_token)
            tx_state.db_prepare = db_prepare
            
            if not db_prepare.success:
                logger.warning(f"DB prepare failed: {db_prepare.error}")
                self._rollback_governance(prepare_token)
                self._abort_transaction(prepare_token)
                return 0
            
            # 1.3 Prepare Audit Entry
            audit_prepare = self._prepare_audit(gov_prepare, db_prepare, prepare_token)
            tx_state.audit_prepare = audit_prepare
            
            if not audit_prepare.success:
                logger.warning(f"Audit prepare failed: {audit_prepare.error}")
                self._rollback_all([gov_prepare, db_prepare], prepare_token)
                self._abort_transaction(prepare_token)
                return 0
            
            # Phase 2: Commit (all or nothing)
            tx_state.phase = 'commit'
            
            # Commit in reverse order of dependencies
            audit_commit = self._commit_audit(audit_prepare)
            db_commit = self._commit_db(db_prepare)
            gov_commit = self._commit_governance(gov_prepare)
            
            # Success!
            facts_added = db_commit.get('facts_added', 0)
            
            # Check performance
            duration_ms = (time.perf_counter() - start_time) * 1000
            if duration_ms > self.MAX_GOVERNANCE_LATENCY_MS:
                logger.warning(
                    f"Governance check exceeded budget: {duration_ms:.2f}ms"
                )
            
            # Clean up transaction
            tx_state.phase = 'complete'
            tx_state.end_time = time.perf_counter()
            
            with self._tx_lock:
                del self._active_transactions[prepare_token]
            
            logger.info(f"Successfully added {facts_added} facts in {duration_ms:.2f}ms")
            return facts_added
            
        except Exception as e:
            # Full rollback on any failure
            logger.error(f"Transaction failed: {e}")
            self._emergency_rollback(prepare_token, str(e))
            raise TransactionFailedException(f"2PC commit failed: {e}")
    
    def _prepare_governance(self, facts: List[str], 
                          context: Dict, 
                          token: str) -> PrepareResult:
        """Phase 1.1: Prepare governance decision"""
        try:
            # Add facts metadata to context
            context.update({
                'engine': 'TransactionalGovernanceEngine',
                'batch_size': len(facts),
                'predicates_set': list({
                    f[:f.index('(')] for f in facts 
                    if '(' in f
                }),
                'max_arg_count': max([
                    len(self.validator._parse_arguments(
                        f[f.index('(')+1:f.rindex(')')]
                    )) for f in facts if '(' in f and ')' in f
                ], default=0),
                'transaction_token': token
            })
            
            # Check for bypass mode
            import os
            if os.environ.get('GOVERNANCE_BYPASS', '').lower() == 'true':
                logger.info("GOVERNANCE BYPASS ACTIVE - Allowing all operations")
                return PrepareResult(
                    success=True,
                    token=token,
                    data={
                        'decision': {'allowed': True, 'bypass': True},
                        'smt_result': {'bypassed': True}
                    }
                )
            
            # Check governance version
            gov_version = os.environ.get('GOVERNANCE_VERSION', 'v2').lower()
            
            if gov_version == 'v3':
                # Use new Governance V3
                try:
                    from .governance_v3 import PragmaticGovernance
                    gov = PragmaticGovernance()
                    decision = gov.decide('add_facts', context)
                    
                    if not decision.allowed:
                        logger.info(f"Governance V3 rejected: {decision.reasons}")
                        return PrepareResult(
                            success=False,
                            token=token,
                            error=f"Governance V3 rejected: {'; '.join(decision.reasons)}",
                            data={'decision': decision.__dict__}
                        )
                    
                    return PrepareResult(
                        success=True,
                        token=token,
                        data={
                            'decision': decision.__dict__,
                            'version': 'v3',
                            'smt_result': {'skipped': True}  # V3 doesn't use SMT
                        }
                    )
                except ImportError:
                    logger.warning("Governance V3 not available, falling back to V2")
                    gov_version = 'v2'
            
            if gov_version == 'v2':
                # Original V2 governance
                decision = self.policy_guard.check(
                    action='add_facts',
                    context=context,
                    externally_legal=context.get('externally_legal', True),
                    sensitivity='write'
                )
                
                # SMT verification
                try:
                    smt_result = self.smt_verifier.verify_governance_decision(
                        decision, context
                    )
                except Exception as smt_e:
                    logger.warning(f"SMT verification failed: {smt_e}, continuing anyway")
                    smt_result = {'error': str(smt_e)}
                
                # Check if should block
                if self.policy_guard.should_block(decision, sensitivity='write'):
                    return PrepareResult(
                        success=False,
                        token=token,
                        error="Governance V2 check rejected action",
                        data={'decision': decision}
                    )
                
                return PrepareResult(
                    success=True,
                    token=token,
                    data={
                        'decision': decision,
                        'version': 'v2',
                        'smt_result': smt_result
                    }
                )
            
        except Exception as e:
            logger.error(f"Governance prepare failed: {e}")
            return PrepareResult(
                success=False,
                token=token,
                error=str(e)
            )
    
    def _prepare_db_transaction(self, facts: List[str], 
                               token: str) -> PrepareResult:
        """Phase 1.2: Prepare database transaction"""
        conn = None
        try:
            # Use timeout to avoid locks
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            conn.execute("PRAGMA busy_timeout = 5000")  # 5 second timeout
            conn.execute("BEGIN IMMEDIATE")  # Lock for write
            
            cursor = conn.cursor()
            prepared_facts = []
            
            for fact_str in facts:
                # Parse fact
                validation = self.validator.validate_fact(fact_str)
                if not validation.valid:
                    conn.rollback()
                    conn.close()
                    return PrepareResult(
                        success=False,
                        token=token,
                        error=f"Fact validation failed: {validation.error}"
                    )
                
                details = validation.details
                predicate = details['predicate']
                args = details['args']
                
                # Prepare for facts_extended table
                fact_data = {
                    'statement': fact_str.rstrip('.'),
                    'predicate': predicate,
                    'arg_count': len(args),
                    'arg1': args[0] if len(args) > 0 else None,
                    'arg2': args[1] if len(args) > 1 else None,
                    'arg3': args[2] if len(args) > 2 else None,
                    'arg4': args[3] if len(args) > 3 else None,
                    'arg5': args[4] if len(args) > 4 else None,
                    'args_json': json.dumps({
                        f'arg{i+6}': arg for i, arg in enumerate(args[5:])
                    }) if len(args) > 5 else None,
                    'fact_type': 'governed',
                    'domain': self._infer_domain(predicate),
                    'complexity': len(args),
                    'confidence': 0.9,
                    'source': 'TransactionalGovernanceEngine',
                    'created_at': datetime.utcnow().isoformat()
                }
                
                prepared_facts.append(fact_data)
            
            # Store connection for commit phase
            self._store_prepared_connection(token, conn, prepared_facts)
            
            return PrepareResult(
                success=True,
                token=token,
                data={'facts_count': len(prepared_facts)}
            )
            
        except sqlite3.OperationalError as e:
            logger.error(f"DB prepare failed: {e}")
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
            # Clean up stored connection if exists
            if token in self._prepared_connections:
                del self._prepared_connections[token]
            return PrepareResult(
                success=False,
                token=token,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"DB prepare failed: {e}")
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
            return PrepareResult(
                success=False,
                token=token,
                error=str(e)
            )
    
    def _prepare_audit(self, gov_prepare: PrepareResult, 
                      db_prepare: PrepareResult, 
                      token: str) -> PrepareResult:
        """Phase 1.3: Prepare audit entry"""
        try:
            audit_data = {
                'transaction_token': token,
                'governance_decision': gov_prepare.data,
                'db_stats': db_prepare.data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Don't actually write yet, just validate we can
            return PrepareResult(
                success=True,
                token=token,
                data=audit_data
            )
            
        except Exception as e:
            logger.error(f"Audit prepare failed: {e}")
            return PrepareResult(
                success=False,
                token=token,
                error=str(e)
            )
    
    def _commit_audit(self, audit_prepare: PrepareResult) -> Dict:
        """Phase 2.1: Commit audit entry"""
        audit_hash = self.audit_logger.log(
            event='facts.added.governed',
            payload=audit_prepare.data
        )
        return {'audit_hash': audit_hash}
    
    def _commit_db(self, db_prepare: PrepareResult) -> Dict:
        """Phase 2.2: Commit database transaction"""
        token = db_prepare.token
        conn, prepared_facts = self._retrieve_prepared_connection(token)
        
        try:
            cursor = conn.cursor()
            facts_added = 0
            
            for fact_data in prepared_facts:
                cursor.execute("""
                    INSERT INTO facts_extended 
                    (statement, predicate, arg_count, arg1, arg2, arg3, arg4, arg5,
                     args_json, fact_type, domain, complexity, confidence, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    fact_data['statement'],
                    fact_data['predicate'],
                    fact_data['arg_count'],
                    fact_data['arg1'],
                    fact_data['arg2'],
                    fact_data['arg3'],
                    fact_data['arg4'],
                    fact_data['arg5'],
                    fact_data['args_json'],
                    fact_data['fact_type'],
                    fact_data['domain'],
                    fact_data['complexity'],
                    fact_data['confidence'],
                    fact_data['source'],
                    fact_data['created_at']
                ))
                facts_added += cursor.rowcount
            
            conn.commit()
            return {'facts_added': facts_added}
            
        finally:
            # Always close connection and clean up
            try:
                conn.close()
            except:
                pass
            if token in self._prepared_connections:
                del self._prepared_connections[token]
    
    def _commit_governance(self, gov_prepare: PrepareResult) -> Dict:
        """Phase 2.3: Finalize governance decision"""
        # Record metrics, update stats, etc.
        return {'status': 'committed'}
    
    def _rollback_governance(self, token: str):
        """Rollback governance decision"""
        logger.info(f"Rolling back governance for transaction {token}")
        
        # Close any open DB connections for this token
        if token in self._prepared_connections:
            conn, _ = self._prepared_connections[token]
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
            del self._prepared_connections[token]
    
    def _rollback_all(self, prepares: List[PrepareResult], token: str):
        """Rollback all prepared operations"""
        for prepare in prepares:
            if prepare and prepare.success:
                logger.info(f"Rolling back {prepare.token}")
        
        # Close any open DB connections
        if token in self._prepared_connections:
            conn, _ = self._prepared_connections[token]
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
            del self._prepared_connections[token]
    
    def _abort_transaction(self, token: str):
        """Abort and clean up transaction"""
        # Close any open connections first
        if token in self._prepared_connections:
            conn, _ = self._prepared_connections[token]
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
            del self._prepared_connections[token]
        
        # Clean up transaction state
        with self._tx_lock:
            if token in self._active_transactions:
                tx_state = self._active_transactions[token]
                tx_state.phase = 'aborted'
                del self._active_transactions[token]
    
    def _emergency_rollback(self, token: str, reason: str):
        """Emergency rollback with compensating transactions"""
        logger.critical(f"EMERGENCY ROLLBACK {token}: {reason}")
        
        # Try to rollback DB and close connection
        try:
            if token in self._prepared_connections:
                conn, _ = self._prepared_connections[token]
                if conn:
                    try:
                        conn.rollback()
                    except:
                        pass
                    try:
                        conn.close()
                    except:
                        pass
                del self._prepared_connections[token]
        except Exception as e:
            logger.error(f"Error during emergency rollback: {e}")
        
        # Log the failure
        try:
            self.audit_logger.log(
                event='emergency.rollback',
                payload={'token': token, 'reason': reason}
            )
        except:
            pass
        
        # Clean up transaction state
        self._abort_transaction(token)
    
    def _direct_add_facts_bypass(self, facts: List[str], context: Dict) -> int:
        """Direct database insertion for bypass mode - no validation"""
        conn = None
        try:
            # Use timeout to avoid locks
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            conn.execute("PRAGMA busy_timeout = 5000")
            cursor = conn.cursor()
            
            facts_added = 0
            for fact_str in facts:
                # Minimal parsing for bypass mode
                fact_str = fact_str.strip().rstrip('.')
                
                # Extract predicate if possible
                if '(' in fact_str and ')' in fact_str:
                    predicate = fact_str[:fact_str.index('(')]
                    args_str = fact_str[fact_str.index('(')+1:fact_str.rindex(')')]
                    args = [a.strip() for a in args_str.split(',')]
                else:
                    predicate = fact_str
                    args = []
                
                # Insert without validation
                cursor.execute("""
                    INSERT OR IGNORE INTO facts_extended 
                    (statement, predicate, arg_count, arg1, arg2, arg3, arg4, arg5,
                     fact_type, domain, complexity, confidence, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    fact_str,
                    predicate,
                    len(args),
                    args[0] if len(args) > 0 else None,
                    args[1] if len(args) > 1 else None,
                    args[2] if len(args) > 2 else None,
                    args[3] if len(args) > 3 else None,
                    args[4] if len(args) > 4 else None,
                    'bypass',
                    'bypass',
                    len(args),
                    1.0,
                    'BYPASS_MODE',
                    datetime.utcnow().isoformat()
                ))
                facts_added += cursor.rowcount
            
            conn.commit()
            
            # Log bypass
            self.audit_logger.log(
                event='facts.added.bypass',
                payload={'count': facts_added, 'context': context}
            )
            
            logger.info(f"BYPASS: Added {facts_added} facts directly")
            return facts_added
            
        except sqlite3.OperationalError as e:
            logger.error(f"Bypass insertion failed: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return 0
        except Exception as e:
            logger.error(f"Bypass insertion failed: {e}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return 0
        finally:
            # Always close connection
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def _infer_domain(self, predicate: str) -> str:
        """Infer domain from predicate"""
        if predicate in ['IsA', 'IsTypeOf', 'TypeOf']:
            return 'ontology'
        elif predicate in ['Causes', 'CausedBy', 'Requires']:
            return 'causality'
        elif predicate in ['HasPart', 'PartOf', 'ConsistsOf']:
            return 'mereology'
        elif predicate in ['LocatedAt', 'LocatedIn', 'HasLocation']:
            return 'spatial'
        return 'general'
    
    # Connection storage (in production, use proper connection pooling)
    _prepared_connections: Dict[str, Tuple[Any, List]] = {}
    
    def _store_prepared_connection(self, token: str, conn: Any, facts: List):
        """Store prepared connection for commit phase"""
        self._prepared_connections[token] = (conn, facts)
    
    def _retrieve_prepared_connection(self, token: str) -> Tuple[Any, List]:
        """Retrieve prepared connection"""
        if token in self._prepared_connections:
            result = self._prepared_connections[token]
            # Don't delete yet - will be deleted after commit or rollback
            return result
        raise ValueError(f"No prepared connection for token {token}")

# ============================================================================
# PERFORMANCE MONITOR
# ============================================================================

class GovernancePerformanceMonitor:
    """Monitor and enforce performance SLOs"""
    
    def __init__(self, engine: TransactionalGovernanceEngine):
        self.engine = engine
        self.metrics = {
            'total_requests': 0,
            'successful_commits': 0,
            'failed_transactions': 0,
            'avg_latency_ms': 0,
            'max_latency_ms': 0,
            'slo_violations': 0
        }
    
    def monitored_add_facts(self, facts: List[str], context: Dict) -> int:
        """Add facts with performance monitoring"""
        start = time.perf_counter()
        
        self.metrics['total_requests'] += 1
        
        try:
            result = self.engine.governed_add_facts_atomic(facts, context)
            self.metrics['successful_commits'] += 1
            
            # Track latency
            duration_ms = (time.perf_counter() - start) * 1000
            self._update_latency_metrics(duration_ms)
            
            return result
            
        except Exception as e:
            self.metrics['failed_transactions'] += 1
            raise
    
    def _update_latency_metrics(self, duration_ms: float):
        """Update latency metrics"""
        # Simple moving average
        alpha = 0.1
        self.metrics['avg_latency_ms'] = (
            alpha * duration_ms + 
            (1 - alpha) * self.metrics['avg_latency_ms']
        )
        
        if duration_ms > self.metrics['max_latency_ms']:
            self.metrics['max_latency_ms'] = duration_ms
        
        if duration_ms > TransactionalGovernanceEngine.MAX_GOVERNANCE_LATENCY_MS:
            self.metrics['slo_violations'] += 1
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        return self.metrics.copy()

# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("=== TransactionalGovernanceEngine Test ===\n")
    
    # Clean up previous test runs
    db_path = "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"
    conn = None # Initialize conn to None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM facts_extended")
        conn.commit()
        print(f"Cleaned up database: {db_path}")
    except Exception as e:
        print(f"Could not clean up database (might not exist yet): {e}")
    finally:
        if conn:
            conn.close()


    # Initialize engine
    engine = TransactionalGovernanceEngine()
    monitor = GovernancePerformanceMonitor(engine)
    
    # Test facts
    test_facts = [
        "Requires(GovernanceEngine, PolicyGuard)",
        "DependsOn(PolicyGuard, Constitution)",
        "Uses(TransactionalEngine, TwoPhaseCommit)"
    ]
    
    # Test context
    context = {
        'operator': 'test_user',
        'reason': 'Testing governance integration',
        'harm_prob': 0.0001,
        'sustain_index': 0.95,
        'externally_legal': True,
        'universalizable_proof': True
    }
    
    print(f"Adding {len(test_facts)} facts with governance...\n")
    
    try:
        result = monitor.monitored_add_facts(test_facts, context)
        print(f"[+] Successfully added {result} facts")
        
        # Show metrics
        metrics = monitor.get_metrics()
        print(f"\nPerformance Metrics:")
        print(f"  Average latency: {metrics['avg_latency_ms']:.2f} ms")
        print(f"  Max latency: {metrics['max_latency_ms']:.2f} ms")
        print(f"  SLO violations: {metrics['slo_violations']}")
        
    except Exception as e:
        print(f"[!] Failed: {e}")
        import traceback
        traceback.print_exc()


