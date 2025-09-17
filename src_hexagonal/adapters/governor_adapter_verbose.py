"""
Governor Adapter für Hexagonal Architecture - ULTRA VERBOSE VERSION
=====================================================================
Nach HAK/GAL Verfassung: Thompson Sampling Strategy Layer
Now with MAXIMUM VISIBILITY into what's happening!
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

# Configure VERBOSE logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GovernorAdapter")


class GovernorAdapter:
    """
    Governor for HEXAGONAL System with integrated learning engines
    Manages Aethelred and Thesis engines for autonomous learning
    NOW WITH MAXIMUM VERBOSITY!
    """
    
    def __init__(self):
        print("\n" + "🎯"*40)
        print("INITIALIZING HEXAGONAL GOVERNOR")
        print("🎯"*40 + "\n")
        
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
        print("🔍 Checking engine files:")
        for name, path in self.engine_paths.items():
            if not path.exists():
                print(f"   ❌ {name} engine NOT FOUND: {path}")
                logger.warning(f"Engine script not found: {path}")
            else:
                print(f"   ✅ {name} engine found: {path}")
                logger.info(f"✅ Found {name} engine: {path}")
        
        # Governor thread
        self.governor_thread = None
        self.stop_event = threading.Event()
        
        self.initialized = True
        print("\n✅ HEXAGONAL Governor initialized with integrated engines\n")
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
        print(f"\n{'='*60}")
        print(f"ATTEMPTING TO START {engine_name.upper()} ENGINE")
        print(f"Duration: {duration_minutes:.1f} minutes")
        print(f"{'='*60}\n")
        
        if engine_name not in self.engine_paths:
            print(f"❌ Unknown engine: {engine_name}")
            logger.error(f"Unknown engine: {engine_name}")
            return False
        
        engine_path = self.engine_paths[engine_name]
        
        if not engine_path.exists():
            print(f"❌ Engine script not found: {engine_path}")
            logger.error(f"Engine script not found: {engine_path}")
            return False
        
        # Check if engine is already running
        engine_info = self.current_state['engines'][engine_name]
        if engine_info['process'] and engine_info['process'].poll() is None:
            print(f"⚠️  {engine_name} engine is already running (PID: {engine_info['pid']})")
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
            
            print(f"🚀 Starting {engine_name} engine...")
            print(f"   Command: {' '.join(cmd)}")
            logger.info(f"Starting {engine_name} engine for {duration_minutes} minutes")
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Start process WITHOUT capturing output so it shows in console
            process = subprocess.Popen(
                cmd,
                # Don't capture stdout/stderr - let it print to console!
                # stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(1)
            
            # Check if it's still running
            if process.poll() is not None:
                print(f"❌ {engine_name} engine died immediately! Exit code: {process.poll()}")
                return False
            
            # Update state
            engine_info['process'] = process
            engine_info['pid'] = process.pid
            engine_info['last_start'] = time.time()
            engine_info['runs'] += 1
            
            print(f"✅ {engine_name} engine started successfully!")
            print(f"   PID: {process.pid}")
            print(f"   Run #{engine_info['runs']}")
            print(f"{'='*60}\n")
            
            logger.info(f"✅ {engine_name} engine started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {engine_name} engine: {e}")
            logger.error(f"Failed to start {engine_name} engine: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop_engine(self, engine_name: str) -> bool:
        """
        Stop a running engine
        
        Args:
            engine_name: 'aethelred' or 'thesis'
            
        Returns:
            True if engine stopped
        """
        print(f"\n🛑 Stopping {engine_name} engine...")
        
        if engine_name not in self.current_state['engines']:
            return False
        
        engine_info = self.current_state['engines'][engine_name]
        
        if engine_info['process'] and engine_info['process'].poll() is None:
            try:
                engine_info['process'].terminate()
                engine_info['process'].wait(timeout=5)
                print(f"✅ {engine_name} engine stopped")
                logger.info(f"✅ {engine_name} engine stopped")
            except:
                engine_info['process'].kill()
                print(f"⚠️  Had to force kill {engine_name} engine")
                logger.warning(f"Had to force kill {engine_name} engine")
            
            engine_info['process'] = None
            engine_info['pid'] = None
            return True
        
        return False
    
    def governor_loop(self):
        """
        Main governor loop - manages engine activation
        """
        print("\n" + "🎯"*30)
        print("GOVERNOR LOOP STARTED!")
        print("Will make decisions every 30 seconds")
        print("🎯"*30 + "\n")
        logger.info("Governor loop started")
        
        loop_count = 0
        
        while not self.stop_event.is_set():
            loop_count += 1
            
            print(f"\n{'='*80}")
            print(f"GOVERNOR LOOP ITERATION #{loop_count} - {time.strftime('%H:%M:%S')}")
            print(f"{'='*80}")
            
            # Show current state
            print(f"📊 Current State:")
            print(f"   Alpha: {self.current_state['alpha']:.2f}")
            print(f"   Beta: {self.current_state['beta']:.2f}")
            print(f"   Success Rate: {self.current_state['alpha']/(self.current_state['alpha']+self.current_state['beta']):.2%}")
            print(f"   Decisions Made: {self.current_state['decisions_made']}")
            
            # Show engine status
            print(f"\n⚙️  Engine Status:")
            for name, info in self.current_state['engines'].items():
                if info['process'] and info['process'].poll() is None:
                    runtime = time.time() - info['last_start']
                    print(f"   {name}: RUNNING (PID: {info['pid']}, Runtime: {runtime:.1f}s)")
                else:
                    print(f"   {name}: STOPPED (Total runs: {info['runs']})")
            
            # Make strategic decision
            print(f"\n🤔 Making strategic decision...")
            decision = self._make_decision()
            
            print(f"\n📋 Decision:")
            print(f"   Action: {decision['action']}")
            if decision['engine']:
                print(f"   Engine: {decision['engine']}")
                print(f"   Duration: {decision.get('duration', 0):.1f} minutes")
                print(f"   Confidence: {decision['confidence']:.2%}")
            print(f"   Reasoning: {' → '.join(decision['reasoning'])}")
            
            if decision['action'] == 'start_engine':
                engine = decision['engine']
                duration = decision.get('duration', 5)
                
                print(f"\n🚀 Executing decision: Start {engine} for {duration:.1f} minutes")
                
                if self.start_engine(engine, duration):
                    # Update Thompson sampling parameters
                    self.current_state['alpha'] += 0.1
                    self.current_state['decisions_made'] += 1
                    print(f"✅ Decision executed successfully! Alpha increased to {self.current_state['alpha']:.2f}")
                else:
                    self.current_state['beta'] += 0.1
                    print(f"❌ Decision failed! Beta increased to {self.current_state['beta']:.2f}")
            else:
                print(f"⏳ Waiting... (both engines running or cooling down)")
            
            # Check running engines
            self._check_engines()
            
            # Wait before next decision
            print(f"\n💤 Sleeping for 30 seconds until next decision...\n")
            time.sleep(30)  # Check every 30 seconds
        
        print("\n🛑 Governor loop stopped")
        logger.info("Governor loop stopped")
    
    def _make_decision(self) -> Dict[str, Any]:
        """
        Make strategic decision using Thompson Sampling
        
        Returns:
            Decision dictionary
        """
        # Thompson Sampling for engine selection - BALANCED for both engines
        aethelred_score = random.betavariate(
            self.current_state['alpha'] + 3,  # Slightly favor Aethelred for fact generation
            self.current_state['beta'] + 1    # Low beta = high success rate
        )
        
        thesis_score = random.betavariate(
            self.current_state['alpha'] + 2,  # Give Thesis a fair chance
            self.current_state['beta'] + 2    # Moderate beta for thesis analysis
        )
        
        print(f"   Thompson Sampling Scores:")
        print(f"      Aethelred: {aethelred_score:.3f}")
        print(f"      Thesis: {thesis_score:.3f}")
        
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
                    
                    print(f"\n" + "🏁"*30)
                    print(f"{name.upper()} ENGINE COMPLETED!")
                    print(f"   Runtime: {runtime:.1f} seconds ({runtime/60:.1f} minutes)")
                    print(f"   Exit code: {poll} ({'SUCCESS' if poll == 0 else 'FAILED'})")
                    print(f"   Total runs: {info['runs']}")
                    print("🏁"*30 + "\n")
                    
                    logger.info(f"{name} engine finished (runtime: {runtime:.1f}s, exit code: {poll})")
                    
                    info['process'] = None
                    info['pid'] = None
                    
                    # Update Thompson sampling based on exit code
                    if poll == 0:
                        self.current_state['alpha'] += 0.2  # Success
                        print(f"✅ Success! Alpha increased by 0.2 to {self.current_state['alpha']:.2f}")
                    else:
                        self.current_state['beta'] += 0.1  # Failure
                        print(f"❌ Failure! Beta increased by 0.1 to {self.current_state['beta']:.2f}")
    
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
        print("\n" + "🚀"*30)
        print("STARTING HEXAGONAL GOVERNOR!")
        print("🚀"*30 + "\n")
        
        if self.current_state['running']:
            print("⚠️  Governor already running")
            logger.warning("Governor already running")
            return False
        
        self.current_state['running'] = True
        self.stop_event.clear()
        
        # Start governor thread
        self.governor_thread = threading.Thread(target=self.governor_loop, daemon=True)
        self.governor_thread.start()
        
        print("✅ HEXAGONAL Governor started successfully!")
        print("   Thread started, will make decisions every 30 seconds")
        print("   Watch this console for engine activity!\n")
        
        logger.info("✅ HEXAGONAL Governor started")
        return True
    
    def stop(self) -> bool:
        """Stop the Governor"""
        print("\n" + "🛑"*30)
        print("STOPPING HEXAGONAL GOVERNOR")
        print("🛑"*30 + "\n")
        
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
        
        print("✅ HEXAGONAL Governor stopped")
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
        
        print(f"✅ Governor mode set to: {mode}")
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
