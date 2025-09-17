#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GOVERNOR EXTENDED ENGINE ADAPTER
=================================
Integrates extended multi-argument engines with the Governor system
"""

import os
import sys
import subprocess
import logging
from typing import Dict, Any, Optional

# Add paths
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL")

class GovernorExtendedAdapter:
    """
    Adapter for running extended engines through Governor
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.python_path = sys.executable
        self.base_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal"
        
        # Engine configurations
        self.engines = {
            'aethelred_extended': {
                'script': 'infrastructure/engines/aethelred_extended.py',
                'description': 'Multi-argument fact generation (3-5+ args)',
                'default_duration': 0.25,  # hours
                'capabilities': ['multi-arg', 'formulas', 'scientific']
            },
            'aethelred_fast': {
                'script': 'infrastructure/engines/aethelred_fast.py',
                'description': 'Standard fast fact generation',
                'default_duration': 0.25,
                'capabilities': ['standard', 'fast']
            },
            'thesis_fast': {
                'script': 'infrastructure/engines/thesis_fast.py',
                'description': 'Pattern analysis engine',
                'default_duration': 0.25,
                'capabilities': ['analysis', 'patterns']
            }
        }
        
        self.running_processes = {}
    
    def start_engine(self, engine_name: str, duration_minutes: float, port: int = 5001) -> Optional[subprocess.Popen]:
        """
        Start an engine with specified parameters
        
        Args:
            engine_name: Name of the engine to start
            duration_minutes: How long to run
            port: API port to use
            
        Returns:
            Process object if successful
        """
        if engine_name not in self.engines:
            self.logger.error(f"Unknown engine: {engine_name}")
            return None
        
        engine_config = self.engines[engine_name]
        script_path = os.path.join(self.base_path, engine_config['script'])
        
        if not os.path.exists(script_path):
            self.logger.error(f"Engine script not found: {script_path}")
            return None
        
        # Build command
        duration_hours = duration_minutes / 60
        cmd = [
            self.python_path,
            script_path,
            '-d', str(duration_hours),
            '-p', str(port)
        ]
        
        self.logger.info(f"Starting {engine_name}: {' '.join(cmd)}")
        
        try:
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=self.base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            self.running_processes[engine_name] = process
            self.logger.info(f"✓ {engine_name} started (PID: {process.pid})")
            
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start {engine_name}: {e}")
            return None
    
    def stop_engine(self, engine_name: str) -> bool:
        """
        Stop a running engine
        
        Args:
            engine_name: Name of engine to stop
            
        Returns:
            True if stopped successfully
        """
        if engine_name not in self.running_processes:
            self.logger.warning(f"Engine {engine_name} not running")
            return False
        
        process = self.running_processes[engine_name]
        
        try:
            process.terminate()
            process.wait(timeout=5)
            del self.running_processes[engine_name]
            self.logger.info(f"✓ {engine_name} stopped")
            return True
            
        except subprocess.TimeoutExpired:
            process.kill()
            del self.running_processes[engine_name]
            self.logger.warning(f"Force killed {engine_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping {engine_name}: {e}")
            return False
    
    def get_engine_status(self) -> Dict[str, Any]:
        """
        Get status of all engines
        
        Returns:
            Status dictionary
        """
        status = {
            'available_engines': list(self.engines.keys()),
            'running_engines': [],
            'engine_details': {}
        }
        
        for name, config in self.engines.items():
            status['engine_details'][name] = {
                'description': config['description'],
                'capabilities': config['capabilities'],
                'running': name in self.running_processes
            }
            
            if name in self.running_processes:
                process = self.running_processes[name]
                status['running_engines'].append(name)
                status['engine_details'][name]['pid'] = process.pid
                status['engine_details'][name]['alive'] = process.poll() is None
        
        return status
    
    def decide_engine(self, context: Dict[str, Any]) -> str:
        """
        Decide which engine to use based on context
        
        Args:
            context: Decision context
            
        Returns:
            Engine name to use
        """
        # Check for specific requirements
        if context.get('require_multi_arg', False):
            return 'aethelred_extended'
        
        if context.get('require_analysis', False):
            return 'thesis_fast'
        
        # Check current database state
        multi_arg_ratio = context.get('multi_arg_ratio', 0)
        
        # If we have few multi-arg facts, prioritize extended engine
        if multi_arg_ratio < 0.1:  # Less than 10% multi-arg
            return 'aethelred_extended'
        
        # Default to standard fast engine
        return 'aethelred_fast'
    
    def get_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations for engine usage
        
        Returns:
            Recommendations dictionary
        """
        recommendations = {
            'strategy': 'balanced',
            'priorities': [],
            'schedule': []
        }
        
        # Check database status
        import sqlite3
        db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count facts by type
        cursor.execute("SELECT COUNT(*) FROM facts_extended WHERE arg_count = 2")
        simple_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM facts_extended WHERE arg_count > 2")
        multi_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM formulas")
        formula_count = cursor.fetchone()[0]
        
        conn.close()
        
        total_facts = simple_count + multi_count
        multi_ratio = multi_count / total_facts if total_facts > 0 else 0
        
        # Generate recommendations
        if multi_ratio < 0.05:
            recommendations['strategy'] = 'aggressive_multi'
            recommendations['priorities'] = [
                'Run aethelred_extended for 80% of time',
                'Focus on scientific domains',
                'Generate formulas actively'
            ]
            recommendations['schedule'] = [
                {'engine': 'aethelred_extended', 'duration': 20, 'repeat': 4},
                {'engine': 'thesis_fast', 'duration': 5, 'repeat': 1}
            ]
        elif multi_ratio < 0.2:
            recommendations['strategy'] = 'balanced_growth'
            recommendations['priorities'] = [
                'Balance multi-arg and simple facts',
                'Maintain domain diversity',
                'Regular pattern analysis'
            ]
            recommendations['schedule'] = [
                {'engine': 'aethelred_extended', 'duration': 15, 'repeat': 2},
                {'engine': 'aethelred_fast', 'duration': 10, 'repeat': 2},
                {'engine': 'thesis_fast', 'duration': 5, 'repeat': 1}
            ]
        else:
            recommendations['strategy'] = 'optimize_quality'
            recommendations['priorities'] = [
                'Focus on fact quality over quantity',
                'Deep pattern analysis',
                'Formula validation'
            ]
            recommendations['schedule'] = [
                {'engine': 'thesis_fast', 'duration': 10, 'repeat': 2},
                {'engine': 'aethelred_extended', 'duration': 10, 'repeat': 1},
                {'engine': 'aethelred_fast', 'duration': 5, 'repeat': 1}
            ]
        
        recommendations['statistics'] = {
            'simple_facts': simple_count,
            'multi_arg_facts': multi_count,
            'formulas': formula_count,
            'multi_arg_ratio': f"{multi_ratio*100:.1f}%"
        }
        
        return recommendations


def integrate_with_governor():
    """
    Integrate extended engines with existing Governor
    """
    print("\n" + "="*60)
    print("GOVERNOR INTEGRATION FOR EXTENDED ENGINES")
    print("="*60)
    
    adapter = GovernorExtendedAdapter()
    
    # Get current status
    status = adapter.get_engine_status()
    print("\nAvailable engines:")
    for name, details in status['engine_details'].items():
        caps = ', '.join(details['capabilities'])
        print(f"  - {name}: {details['description']}")
        print(f"    Capabilities: {caps}")
    
    # Get recommendations
    recommendations = adapter.get_recommendations()
    print(f"\nStrategy: {recommendations['strategy']}")
    print(f"Statistics:")
    for key, value in recommendations['statistics'].items():
        print(f"  - {key}: {value}")
    
    print("\nRecommended schedule:")
    for item in recommendations['schedule']:
        print(f"  - Run {item['engine']} for {item['duration']} min (repeat {item['repeat']}x)")
    
    return adapter


def main():
    """Main test"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    adapter = integrate_with_governor()
    
    # Test starting extended engine
    print("\n" + "="*60)
    print("TEST: Starting extended engine")
    print("="*60)
    
    process = adapter.start_engine('aethelred_extended', duration_minutes=1, port=5001)
    
    if process:
        print("✓ Engine started successfully")
        
        # Wait a bit
        import time
        time.sleep(5)
        
        # Check status
        status = adapter.get_engine_status()
        print(f"Running engines: {status['running_engines']}")
        
        # Stop engine
        adapter.stop_engine('aethelred_extended')
        print("✓ Engine stopped")
    else:
        print("✗ Failed to start engine")
    
    print("\n✓ Governor integration ready!")


if __name__ == "__main__":
    main()
