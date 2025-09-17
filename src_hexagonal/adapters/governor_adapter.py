"""
Governor Adapter für Hexagonal Architecture
============================================
Nach HAK/GAL Verfassung: Thompson Sampling Strategy Layer
Now with integrated HEXAGONAL engines
"""

import sys
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import random
import logging
from .llm_governor_decision_engine import LLMGovernorDecisionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GovernorAdapter")


class GovernorAdapter:
    """
    Governor for HEXAGONAL System with integrated learning engines
    Manages Aethelred and Thesis engines for autonomous learning
    """
    
    def __init__(self):
        self.initialized = False
        self.decisions_history = []
        # Get current port from environment or default
        self.port = int(os.environ.get('HAKGAL_PORT', '5001'))
        logger.info(f"Governor using port: {self.port}")
        
        # Define hex_root FIRST (before using it)
        self.hex_root = Path(__file__).parent.parent.parent
        
        self.current_state = {
            'running': False,
            'mode': 'llm_governor',
            'alpha': 1.0,
            'beta': 1.0,
            'decisions_made': 0,
            'engines': {
                'aethelred': {
                    'enabled': True,
                    'process': None,
                    'last_start': None,
                    'runs': 0,
                    'pid': None
                },
                'thesis': {
                    'enabled': True,
                    'process': None,
                    'last_start': None,
                    'runs': 0,
                    'pid': None
                },
                'generator': {
                    'enabled': True,
                    'process': None,
                    'last_start': None,
                    'runs': 0,
                    'pid': None
                }
            }
        }
        
        # Initialize LLM Decision Engine (AFTER hex_root is defined)
        self.llm_decision_engine = LLMGovernorDecisionEngine(
            db_path=str(self.hex_root / 'hexagonal_kb.db')
        )
        self.use_llm_governor = True  # Enable LLM-based decisions by default
        
        # Engine paths in HEXAGONAL system
        self.engine_paths = {
            'aethelred': self.hex_root / 'src_hexagonal' / 'infrastructure' / 'engines' / 'aethelred_extended_fixed.py',
            'thesis': self.hex_root / 'src_hexagonal' / 'infrastructure' / 'engines' / 'thesis_enhanced.py',
            'generator': self.hex_root / 'src_hexagonal' / 'infrastructure' / 'engines' / 'simple_fact_generator.py'
        }
        
        # Verify engine files exist
        for name, path in self.engine_paths.items():
            if not path.exists():
                logger.warning(f"Engine script not found: {path}")
            else:
                logger.info(f"✅ Found {name} engine: {path}")
        
        # Governor thread
        self.governor_thread = None
        self.stop_event = threading.Event()
        
        self.initialized = True
        logger.info("✅ HEXAGONAL Governor initialized with integrated engines")
    
    def start_engine(self, engine_name: str, duration_minutes: float = 5) -> bool:
        print("\n" + "🚀"*40)
        print(f"START_ENGINE CALLED: {engine_name}")
        print(f"Duration: {duration_minutes} minutes")
        print("🚀"*40)
        """
        Start a specific engine as subprocess
        
        Args:
            engine_name: 'aethelred' or 'thesis'
            duration_minutes: How long to run the engine
            
        Returns:
            True if engine started successfully
        """
        if engine_name not in self.engine_paths:
            logger.error(f"Unknown engine: {engine_name}")
            return False
        
        engine_path = self.engine_paths[engine_name]
        
        if not engine_path.exists():
            logger.error(f"Engine script not found: {engine_path}")
            return False
        
        # Check if engine is already running
        engine_info = self.current_state['engines'][engine_name]
        if engine_info['process'] and engine_info['process'].poll() is None:
            logger.warning(f"{engine_name} engine is already running")
            return False
        
        try:
            # NEUE LOGIK: Output direkt in eine Log-Datei umleiten
            log_dir = self.hex_root / 'logs' / 'engine_logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            log_file_path = log_dir / f"{engine_name}_{timestamp}.log"
            
            logger.info(f"Redirecting {engine_name} output to {log_file_path}")
            
            # Öffne die Log-Datei zum Schreiben
            log_file_handle = open(log_file_path, 'w', encoding='utf-8')

            # Start engine subprocess
            # Use different port for engine to avoid conflict with backend
            engine_port = self.port + 1  # Use backend_port + 1
            cmd = [
                sys.executable,  # Python executable
                str(engine_path),
                '-d', str(duration_minutes / 60),  # Convert to hours
                '-p', str(engine_port)  # Use different port to avoid conflict
            ]
            
            logger.info(f"Starting {engine_name} engine for {duration_minutes} minutes on port {engine_port}")
            logger.info(f"Command: {' '.join(cmd)}")
            
            print(f"\n🔥 EXECUTING COMMAND:")
            print(f"  {' '.join(cmd)}")
            print(f"  CWD: {Path.cwd()}")
            print(f"  Engine script exists: {engine_path.exists()}")
            print(f"  Python: {sys.executable}")
            
            process = subprocess.Popen(
                cmd,
                stdout=log_file_handle, # Leite stdout in die Datei um
                stderr=log_file_handle, # Leite stderr in dieselbe Datei um
                text=False # text=True ist nicht kompatibel mit file handle redirection
            )
            
            # Der read_output Thread wird nicht mehr benötigt
            
            # Update state
            engine_info['process'] = process
            engine_info['pid'] = process.pid
            engine_info['last_start'] = time.time()
            engine_info['runs'] += 1
            engine_info['log_file'] = str(log_file_path) # Speichere den Log-Pfad
            
            logger.info(f"✅ {engine_name} engine started (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {engine_name} engine: {e}")
            return False
    
    def stop_engine(self, engine_name: str) -> bool:
        """
        Stop a running engine
        
        Args:
            engine_name: 'aethelred' or 'thesis'
            
        Returns:
            True if engine stopped
        """
        if engine_name not in self.current_state['engines']:
            return False
        
        engine_info = self.current_state['engines'][engine_name]
        
        if engine_info['process'] and engine_info['process'].poll() is None:
            try:
                engine_info['process'].terminate()
                engine_info['process'].wait(timeout=5)
                logger.info(f"✅ {engine_name} engine stopped")
            except:
                engine_info['process'].kill()
                logger.warning(f"Had to force kill {engine_name} engine")
            
            engine_info['process'] = None
            engine_info['pid'] = None
            return True
        
        return False
    
    def governor_loop(self):
        """
        Main governor loop - manages engine activation
        """
        logger.info("Governor loop started")
        
        while not self.stop_event.is_set():
            print(f"\n{'='*60}")
            print(f"GOVERNOR LOOP ITERATION")
            print(f"{'='*60}")
            
            # Make strategic decision
            print("🎯 Making strategic decision...")
            decision = self._make_decision()
            print(f"Decision: {decision}")
            
            if decision['action'] == 'start_engine':
                engine = decision['engine']
                duration = decision.get('duration', 5)
                
                if self.start_engine(engine, duration):
                    # Update Thompson sampling parameters
                    self.current_state['alpha'] += 0.1
                    self.current_state['decisions_made'] += 1
                else:
                    self.current_state['beta'] += 0.1
            
            # Check running engines
            self._check_engines()
            
            # Wait before next decision
            time.sleep(30)  # Check every 30 seconds
        
        logger.info("Governor loop stopped")
    
    def _make_decision(self) -> Dict[str, Any]:
        """
        Make strategic decision using LLM Governor or Thompson Sampling fallback
        
        Returns:
            Decision dictionary
        """
        # Use LLM Governor as primary decision maker
        if self.use_llm_governor:
            try:
                # Prepare engine status for LLM
                engine_status = {
                    'aethelred_running': (
                        self.current_state['engines']['aethelred']['process'] and
                        self.current_state['engines']['aethelred']['process'].poll() is None
                    ),
                    'thesis_running': (
                        self.current_state['engines']['thesis']['process'] and
                        self.current_state['engines']['thesis']['process'].poll() is None
                    ),
                    'aethelred_runs': self.current_state['engines']['aethelred']['runs'],
                    'thesis_runs': self.current_state['engines']['thesis']['runs']
                }
                
                # Get LLM decision
                llm_decision = self.llm_decision_engine.make_decision(engine_status)
                if llm_decision:
                    logger.info(f"🤖 LLM Governor decided: {llm_decision['engine']} "
                               f"(confidence: {llm_decision['confidence']:.2f})")
                    return llm_decision
                else:
                    logger.warning("LLM Governor failed, falling back to Thompson Sampling")
            except Exception as e:
                logger.error(f"LLM Governor error: {e}, falling back to Thompson Sampling")
        
        # Thompson Sampling fallback
        logger.info("📊 Using Thompson Sampling fallback")
        aethelred_score = random.betavariate(
            self.current_state['alpha'] + 3,  # Slightly favor Aethelred for fact generation
            self.current_state['beta'] + 1    # Low beta = high success rate
        )
        
        thesis_score = random.betavariate(
            self.current_state['alpha'] + 2,  # Give Thesis a fair chance
            self.current_state['beta'] + 2    # Moderate beta for thesis analysis
        )
        
        generator_score = random.betavariate(
            self.current_state['alpha'] + 5,  # Favor generator for consistent fact generation
            self.current_state['beta'] + 1    # Low beta = high success rate
        )
        
        # Check which engines are available to start
        aethelred_running = (
            self.current_state['engines']['aethelred']['process'] and
            self.current_state['engines']['aethelred']['process'].poll() is None
        )
        
        thesis_running = (
            self.current_state['engines']['thesis']['process'] and
            self.current_state['engines']['thesis']['process'].poll() is None
        )
        
        generator_running = (
            self.current_state['engines']['generator']['process'] and
            self.current_state['engines']['generator']['process'].poll() is None
        )
        
        decision = {
            'timestamp': time.time(),
            'action': 'wait',
            'engine': None,
            'confidence': 0.0,
            'reasoning': []
        }
        
        # Decide which engine to start - PRIORITIZE GENERATOR
        if not generator_running:
            # ALWAYS start generator first for consistent fact generation
            decision['action'] = 'start_engine'
            decision['engine'] = 'generator'
            decision['duration'] = random.uniform(10, 20)  # 10-20 minutes
            decision['confidence'] = generator_score
            decision['reasoning'] = ['Generator not running', 'Prioritizing fact generation']
        elif not aethelred_running and not thesis_running:
            # No other engines running - start one
            if aethelred_score > thesis_score:
                decision['action'] = 'start_engine'
                decision['engine'] = 'aethelred'
                decision['duration'] = random.uniform(3, 10)  # 3-10 minutes
                decision['confidence'] = aethelred_score
                decision['reasoning'] = ['Generator running', 'No other engines', 'Aethelred scored higher']
            else:
                decision['action'] = 'start_engine'
                decision['engine'] = 'thesis'
                decision['duration'] = random.uniform(5, 15)  # 5-15 minutes
                decision['confidence'] = thesis_score
                decision['reasoning'] = ['Generator running', 'No other engines', 'Thesis scored higher']
        
        elif not aethelred_running and thesis_running:
            # Generator + thesis running - maybe start aethelred
            if aethelred_score > 0.7:
                decision['action'] = 'start_engine'
                decision['engine'] = 'aethelred'
                decision['duration'] = random.uniform(3, 8)
                decision['confidence'] = aethelred_score
                decision['reasoning'] = ['Generator + Thesis running', 'High score for Aethelred']
        
        elif aethelred_running and not thesis_running:
            # Generator + aethelred running - maybe start thesis
            if thesis_score > 0.6:
                decision['action'] = 'start_engine'
                decision['engine'] = 'thesis'
                decision['duration'] = random.uniform(5, 10)
                decision['confidence'] = thesis_score
                decision['reasoning'] = ['Generator + Aethelred running', 'Good score for Thesis']
        
        else:
            # Both running - wait
            decision['reasoning'] = ['Both engines running', 'Waiting for completion']
        
        # Record decision
        self.decisions_history.append(decision)
        
        if decision['action'] != 'wait':
            logger.info(f"Decision: {decision['action']} - {decision['engine']} "
                       f"(confidence: {decision['confidence']:.2f})")
        
        return decision
    
    def _check_engines(self):
        """Check status of running engines"""
        for name, info in self.current_state['engines'].items():
            if info['process']:
                poll = info['process'].poll()
                if poll is not None:
                    # Engine finished
                    runtime = time.time() - info['last_start']
                    logger.info(f"{name} engine finished (runtime: {runtime:.1f}s, exit code: {poll})")
                    
                    # Read output if available
                    try:
                        stdout, stderr = info['process'].communicate(timeout=1)
                        if stdout:
                            logger.debug(f"{name} output: {stdout[-500:]}")  # Last 500 chars
                    except:
                        pass
                    
                    info['process'] = None
                    info['pid'] = None
                    
                    # Update Thompson sampling based on exit code
                    if poll == 0:
                        self.current_state['alpha'] += 0.2  # Success
                    else:
                        self.current_state['beta'] += 0.1  # Failure
    
    def get_status(self) -> Dict[str, Any]:
        """Get current Governor status - JSON serializable"""
        # Manually build status dict without process objects
        status = {
            'running': self.current_state['running'],
            'mode': self.current_state['mode'],
            'alpha': self.current_state['alpha'],
            'beta': self.current_state['beta'],
            'decisions_made': self.current_state['decisions_made'],
            'engines': {}
        }
        
        # Build engine status without process objects
        for name, info in self.current_state['engines'].items():
            engine_status = {
                'enabled': info['enabled'],
                'last_start': info['last_start'],
                'runs': info['runs'],
                'pid': info['pid'],
                'running': False,
                'runtime': None
            }
            
            # Check if engine is running
            if info['process'] and info['process'].poll() is None:
                engine_status['running'] = True
                if info['last_start']:
                    engine_status['runtime'] = time.time() - info['last_start']
            
            status['engines'][name] = engine_status
        
        # Add metrics
        status['success_rate'] = (
            self.current_state['alpha'] / 
            (self.current_state['alpha'] + self.current_state['beta'])
        )
        
        status['decisions_count'] = len(self.decisions_history)
        
        return status
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Governor metrics"""
        metrics = {
            'alpha': self.current_state['alpha'],
            'beta': self.current_state['beta'],
            'success_rate': self.current_state['alpha'] / (
                self.current_state['alpha'] + self.current_state['beta']
            ),
            'decisions_made': self.current_state['decisions_made'],
            'total_runs': {
                'aethelred': self.current_state['engines']['aethelred']['runs'],
                'thesis': self.current_state['engines']['thesis']['runs']
            }
        }
        
        # Add recent decisions
        if self.decisions_history:
            metrics['recent_decisions'] = self.decisions_history[-5:]  # Last 5 decisions
            metrics['last_decision'] = self.decisions_history[-1]
        
        return metrics
    
    def get_next_decision(self) -> Dict[str, Any]:
        """Get next strategic decision"""
        return self._make_decision()
    
    def start(self) -> bool:
        """Start the Governor"""
        if self.current_state['running']:
            logger.warning("Governor already running")
            return False
        
        self.current_state['running'] = True
        self.stop_event.clear()
        
        # Start governor thread
        self.governor_thread = threading.Thread(target=self.governor_loop, daemon=True)
        self.governor_thread.start()
        
        logger.info("✅ HEXAGONAL Governor started")
        return True
    
    def stop(self) -> bool:
        """Stop the Governor"""
        if not self.current_state['running']:
            return False
        
        self.current_state['running'] = False
        self.stop_event.set()
        
        # Stop all engines
        for engine_name in self.current_state['engines']:
            self.stop_engine(engine_name)
        
        # Wait for governor thread
        if self.governor_thread:
            self.governor_thread.join(timeout=5)
        
        logger.info("✅ HEXAGONAL Governor stopped")
        return True
    
    def set_mode(self, mode: str) -> bool:
        """Set Governor mode"""
        valid_modes = ['llm_governor', 'hexagonal', 'thompson_sampling', 'epsilon_greedy', 'random', 'disabled']
        
        if mode not in valid_modes:
            logger.error(f"Invalid mode: {mode}")
            return False
        
        self.current_state['mode'] = mode
        
        if mode == 'disabled':
            self.stop()
        
        logger.info(f"✅ Governor mode set to: {mode}")
        return True
    
    def get_engine_recommendations(self) -> Dict[str, float]:
        """Get engine activation recommendations"""
        return {
            'aethelred': random.betavariate(
                self.current_state['alpha'] + 1,
                self.current_state['beta'] + 1
            ),
            'thesis': random.betavariate(
                self.current_state['alpha'] + 0.5,
                self.current_state['beta'] + 1.5
            )
        }


# Singleton instance
_governor_instance = None

def get_governor_adapter() -> GovernorAdapter:
    """Get or create Governor adapter singleton"""
    global _governor_instance
    if _governor_instance is None:
        _governor_instance = GovernorAdapter()
    return _governor_instance
