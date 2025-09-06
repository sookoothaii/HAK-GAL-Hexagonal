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
import copy

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
        self.current_state = {
            'running': False,
            'mode': 'hexagonal',
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
                }
            }
        }
        
        # Engine paths in HEXAGONAL system
        self.hex_root = Path(__file__).parent.parent.parent
        self.engine_paths = {
            'aethelred': self.hex_root / 'src_hexagonal' / 'infrastructure' / 'engines' / 'aethelred_engine.py',
            'thesis': self.hex_root / 'src_hexagonal' / 'infrastructure' / 'engines' / 'thesis_engine.py'
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
            # Start engine subprocess
            cmd = [
                sys.executable,  # Python executable
                str(engine_path),
                '-d', str(duration_minutes / 60),  # Convert to hours
                '-p', '5001'  # HEXAGONAL port
            ]
            
            logger.info(f"Starting {engine_name} engine for {duration_minutes} minutes")
            logger.info(f"Command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Update state
            engine_info['process'] = process
            engine_info['pid'] = process.pid
            engine_info['last_start'] = time.time()
            engine_info['runs'] += 1
            
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
            # Make strategic decision
            decision = self._make_decision()
            
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
        Make strategic decision using Thompson Sampling
        
        Returns:
            Decision dictionary
        """
        # Thompson Sampling for engine selection
        aethelred_score = random.betavariate(
            self.current_state['alpha'] + 1,
            self.current_state['beta'] + 1
        )
        
        thesis_score = random.betavariate(
            self.current_state['alpha'] + 0.5,
            self.current_state['beta'] + 1.5
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
        
        decision = {
            'timestamp': time.time(),
            'action': 'wait',
            'engine': None,
            'confidence': 0.0,
            'reasoning': []
        }
        
        # Decide which engine to start
        if not aethelred_running and not thesis_running:
            # No engines running - start one
            if aethelred_score > thesis_score:
                decision['action'] = 'start_engine'
                decision['engine'] = 'aethelred'
                decision['duration'] = random.uniform(3, 10)  # 3-10 minutes
                decision['confidence'] = aethelred_score
                decision['reasoning'] = ['No engines running', 'Aethelred scored higher']
            else:
                decision['action'] = 'start_engine'
                decision['engine'] = 'thesis'
                decision['duration'] = random.uniform(5, 15)  # 5-15 minutes
                decision['confidence'] = thesis_score
                decision['reasoning'] = ['No engines running', 'Thesis scored higher']
        
        elif not aethelred_running and thesis_running:
            # Only thesis running - maybe start aethelred
            if aethelred_score > 0.7:
                decision['action'] = 'start_engine'
                decision['engine'] = 'aethelred'
                decision['duration'] = random.uniform(3, 8)
                decision['confidence'] = aethelred_score
                decision['reasoning'] = ['Thesis already running', 'High score for Aethelred']
        
        elif aethelred_running and not thesis_running:
            # Only aethelred running - maybe start thesis
            if thesis_score > 0.6:
                decision['action'] = 'start_engine'
                decision['engine'] = 'thesis'
                decision['duration'] = random.uniform(5, 10)
                decision['confidence'] = thesis_score
                decision['reasoning'] = ['Aethelred already running', 'Good score for Thesis']
        
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
        # Create deep copy to avoid modifying original
        status = copy.deepcopy(self.current_state)
        
        # Remove non-serializable process objects and add serializable info
        for name, info in status['engines'].items():
            # Remove process object - not JSON serializable
            if 'process' in info:
                del info['process']
            
            # Add running status based on original state
            orig_info = self.current_state['engines'][name]
            info['running'] = (
                orig_info['process'] is not None and 
                orig_info['process'].poll() is None
            )
            
            # Add runtime if running
            if info['running'] and info['last_start']:
                info['runtime'] = time.time() - info['last_start']
            
            # Keep PID if available (it's just an integer)
            info['pid'] = orig_info.get('pid')
        
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
        valid_modes = ['hexagonal', 'thompson_sampling', 'epsilon_greedy', 'random', 'disabled']
        
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
