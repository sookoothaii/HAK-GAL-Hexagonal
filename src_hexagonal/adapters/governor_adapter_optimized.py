"""
Optimized Governor Adapter mit Thompson Sampling
=================================================
Nach HAK/GAL Verfassung Artikel 2: Strategische Entscheidungsfindung
Mit Performance-Optimierungen und erweiterten Features
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import threading
import time
from collections import deque
import math

@dataclass
class Arm:
    """Represents an arm in the multi-armed bandit"""
    id: str
    name: str
    alpha: float = 1.0  # Success count + 1
    beta: float = 1.0   # Failure count + 1
    pulls: int = 0
    successes: int = 0
    failures: int = 0
    last_pull: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def sample(self) -> float:
        """Sample from Beta distribution"""
        return np.random.beta(self.alpha, self.beta)
    
    def update(self, reward: bool):
        """Update arm statistics with reward"""
        self.pulls += 1
        if reward:
            self.successes += 1
            self.alpha += 1
        else:
            self.failures += 1
            self.beta += 1
        self.last_pull = datetime.now()
    
    def get_confidence_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """Get confidence interval for expected reward"""
        from scipy import stats
        lower = stats.beta.ppf((1 - confidence) / 2, self.alpha, self.beta)
        upper = stats.beta.ppf((1 + confidence) / 2, self.alpha, self.beta)
        return lower, upper
    
    def get_expected_reward(self) -> float:
        """Get expected reward (mean of Beta distribution)"""
        return self.alpha / (self.alpha + self.beta)

@dataclass
class Decision:
    """Represents a decision made by the Governor"""
    id: str
    arm_id: str
    arm_name: str
    timestamp: datetime
    sampled_value: float
    expected_reward: float
    confidence_interval: Tuple[float, float]
    exploration_bonus: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class OptimizedGovernor:
    """
    Optimized Thompson Sampling Governor for HAK-GAL
    Features:
    - Pure Thompson Sampling
    - UCB (Upper Confidence Bound) mode
    - Epsilon-Greedy mode
    - Contextual bandits support
    - Batch decision making
    - Performance metrics tracking
    """
    
    def __init__(self, mode: str = 'thompson_sampling'):
        self.mode = mode
        self.arms: Dict[str, Arm] = {}
        self.decisions: deque = deque(maxlen=1000)  # Keep last 1000 decisions
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
        # Performance metrics
        self.metrics = {
            'total_decisions': 0,
            'total_reward': 0,
            'cumulative_regret': 0,
            'start_time': None,
            'last_decision_time': None,
            'decision_times_ms': deque(maxlen=100)
        }
        
        # Configuration
        self.config = {
            'exploration_rate': 0.1,  # For epsilon-greedy
            'ucb_c': 2.0,  # Exploration parameter for UCB
            'decay_factor': 0.995,  # For decaying exploration
            'batch_size': 10,  # For batch decisions
            'min_samples': 5  # Minimum samples before exploitation
        }
        
        # Initialize default arms for HAK-GAL system
        self._initialize_default_arms()
    
    def _initialize_default_arms(self):
        """Initialize default arms for HAK-GAL decision making"""
        default_arms = [
            {
                'id': 'llm_deepseek',
                'name': 'DeepSeek LLM Provider',
                'metadata': {'type': 'llm', 'cost': 'low', 'speed': 'fast'}
            },
            {
                'id': 'llm_gemini',
                'name': 'Gemini LLM Provider',
                'metadata': {'type': 'llm', 'cost': 'medium', 'speed': 'medium'}
            },
            {
                'id': 'llm_mistral',
                'name': 'Mistral LLM Provider',
                'metadata': {'type': 'llm', 'cost': 'high', 'speed': 'slow'}
            },
            {
                'id': 'cache_aggressive',
                'name': 'Aggressive Caching Strategy',
                'metadata': {'type': 'cache', 'memory': 'high', 'hit_rate': 'high'}
            },
            {
                'id': 'cache_moderate',
                'name': 'Moderate Caching Strategy',
                'metadata': {'type': 'cache', 'memory': 'medium', 'hit_rate': 'medium'}
            },
            {
                'id': 'cache_minimal',
                'name': 'Minimal Caching Strategy',
                'metadata': {'type': 'cache', 'memory': 'low', 'hit_rate': 'low'}
            },
            {
                'id': 'batch_small',
                'name': 'Small Batch Processing',
                'metadata': {'type': 'batch', 'size': 10, 'latency': 'low'}
            },
            {
                'id': 'batch_medium',
                'name': 'Medium Batch Processing',
                'metadata': {'type': 'batch', 'size': 50, 'latency': 'medium'}
            },
            {
                'id': 'batch_large',
                'name': 'Large Batch Processing',
                'metadata': {'type': 'batch', 'size': 100, 'latency': 'high'}
            }
        ]
        
        for arm_config in default_arms:
            arm = Arm(
                id=arm_config['id'],
                name=arm_config['name'],
                metadata=arm_config.get('metadata', {})
            )
            self.arms[arm.id] = arm
    
    def add_arm(self, arm_id: str, name: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a new arm to the bandit"""
        with self.lock:
            if arm_id not in self.arms:
                self.arms[arm_id] = Arm(
                    id=arm_id,
                    name=name,
                    metadata=metadata or {}
                )
                return True
            return False
    
    def remove_arm(self, arm_id: str) -> bool:
        """Remove an arm from the bandit"""
        with self.lock:
            if arm_id in self.arms:
                del self.arms[arm_id]
                return True
            return False
    
    def _thompson_sampling_decision(self) -> Optional[Decision]:
        """Make decision using Thompson Sampling"""
        if not self.arms:
            return None
        
        # Sample from each arm
        samples = {}
        for arm_id, arm in self.arms.items():
            samples[arm_id] = arm.sample()
        
        # Select arm with highest sample
        best_arm_id = max(samples, key=samples.get)
        best_arm = self.arms[best_arm_id]
        
        # Create decision
        decision = Decision(
            id=f"ts_{self.metrics['total_decisions']}_{int(time.time())}",
            arm_id=best_arm_id,
            arm_name=best_arm.name,
            timestamp=datetime.now(),
            sampled_value=samples[best_arm_id],
            expected_reward=best_arm.get_expected_reward(),
            confidence_interval=best_arm.get_confidence_interval(),
            metadata={'mode': 'thompson_sampling', 'all_samples': samples}
        )
        
        return decision
    
    def _ucb_decision(self) -> Optional[Decision]:
        """Make decision using Upper Confidence Bound"""
        if not self.arms:
            return None
        
        total_pulls = sum(arm.pulls for arm in self.arms.values())
        if total_pulls == 0:
            # Random selection for first pull
            arm_id = np.random.choice(list(self.arms.keys()))
            arm = self.arms[arm_id]
            return Decision(
                id=f"ucb_{self.metrics['total_decisions']}_{int(time.time())}",
                arm_id=arm_id,
                arm_name=arm.name,
                timestamp=datetime.now(),
                sampled_value=0.5,
                expected_reward=0.5,
                confidence_interval=(0, 1),
                exploration_bonus=float('inf'),
                metadata={'mode': 'ucb', 'reason': 'initial_exploration'}
            )
        
        # Calculate UCB values
        ucb_values = {}
        for arm_id, arm in self.arms.items():
            if arm.pulls == 0:
                ucb_values[arm_id] = float('inf')
            else:
                exploitation = arm.get_expected_reward()
                exploration = self.config['ucb_c'] * math.sqrt(
                    2 * math.log(total_pulls) / arm.pulls
                )
                ucb_values[arm_id] = exploitation + exploration
        
        # Select arm with highest UCB
        best_arm_id = max(ucb_values, key=ucb_values.get)
        best_arm = self.arms[best_arm_id]
        
        return Decision(
            id=f"ucb_{self.metrics['total_decisions']}_{int(time.time())}",
            arm_id=best_arm_id,
            arm_name=best_arm.name,
            timestamp=datetime.now(),
            sampled_value=ucb_values[best_arm_id],
            expected_reward=best_arm.get_expected_reward(),
            confidence_interval=best_arm.get_confidence_interval(),
            exploration_bonus=ucb_values[best_arm_id] - best_arm.get_expected_reward(),
            metadata={'mode': 'ucb', 'all_ucb_values': ucb_values}
        )
    
    def _epsilon_greedy_decision(self) -> Optional[Decision]:
        """Make decision using Epsilon-Greedy strategy"""
        if not self.arms:
            return None
        
        # Decay exploration rate over time
        current_epsilon = self.config['exploration_rate'] * (
            self.config['decay_factor'] ** self.metrics['total_decisions']
        )
        
        if np.random.random() < current_epsilon:
            # Explore: random selection
            arm_id = np.random.choice(list(self.arms.keys()))
            reason = 'exploration'
        else:
            # Exploit: select best arm
            arm_id = max(
                self.arms.keys(),
                key=lambda x: self.arms[x].get_expected_reward()
            )
            reason = 'exploitation'
        
        arm = self.arms[arm_id]
        
        return Decision(
            id=f"eg_{self.metrics['total_decisions']}_{int(time.time())}",
            arm_id=arm_id,
            arm_name=arm.name,
            timestamp=datetime.now(),
            sampled_value=arm.get_expected_reward(),
            expected_reward=arm.get_expected_reward(),
            confidence_interval=arm.get_confidence_interval(),
            exploration_bonus=current_epsilon,
            metadata={'mode': 'epsilon_greedy', 'epsilon': current_epsilon, 'reason': reason}
        )
    
    def get_next_decision(self) -> Optional[Decision]:
        """Get next decision based on current mode"""
        start_time = time.time()
        
        with self.lock:
            if self.mode == 'thompson_sampling':
                decision = self._thompson_sampling_decision()
            elif self.mode == 'ucb':
                decision = self._ucb_decision()
            elif self.mode == 'epsilon_greedy':
                decision = self._epsilon_greedy_decision()
            else:
                # Default to Thompson Sampling
                decision = self._thompson_sampling_decision()
            
            if decision:
                # Update metrics
                self.metrics['total_decisions'] += 1
                self.metrics['last_decision_time'] = datetime.now()
                decision_time_ms = (time.time() - start_time) * 1000
                self.metrics['decision_times_ms'].append(decision_time_ms)
                
                # Store decision
                self.decisions.append(decision)
                
                # Don't actually pull the arm here - wait for feedback
        
        return decision
    
    def get_batch_decisions(self, batch_size: Optional[int] = None) -> List[Decision]:
        """Get multiple decisions at once"""
        batch_size = batch_size or self.config['batch_size']
        decisions = []
        
        for _ in range(batch_size):
            decision = self.get_next_decision()
            if decision:
                decisions.append(decision)
        
        return decisions
    
    def update_arm(self, arm_id: str, reward: bool) -> bool:
        """Update arm with reward feedback"""
        with self.lock:
            if arm_id in self.arms:
                self.arms[arm_id].update(reward)
                self.metrics['total_reward'] += int(reward)
                
                # Calculate regret (assuming best arm has 0.9 expected reward)
                best_possible = 0.9
                actual = self.arms[arm_id].get_expected_reward()
                self.metrics['cumulative_regret'] += (best_possible - actual)
                
                return True
            return False
    
    def get_arm_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics for all arms"""
        with self.lock:
            stats = {}
            for arm_id, arm in self.arms.items():
                stats[arm_id] = {
                    'name': arm.name,
                    'pulls': arm.pulls,
                    'successes': arm.successes,
                    'failures': arm.failures,
                    'expected_reward': arm.get_expected_reward(),
                    'confidence_interval': arm.get_confidence_interval(),
                    'alpha': arm.alpha,
                    'beta': arm.beta,
                    'last_pull': arm.last_pull.isoformat() if arm.last_pull else None,
                    'metadata': arm.metadata
                }
            return stats
    
    def get_status(self) -> Dict[str, Any]:
        """Get Governor status"""
        with self.lock:
            avg_decision_time = (
                np.mean(self.metrics['decision_times_ms'])
                if self.metrics['decision_times_ms'] else 0
            )
            
            return {
                'running': self.running,
                'mode': self.mode,
                'total_arms': len(self.arms),
                'total_decisions': self.metrics['total_decisions'],
                'total_reward': self.metrics['total_reward'],
                'success_rate': (
                    self.metrics['total_reward'] / self.metrics['total_decisions']
                    if self.metrics['total_decisions'] > 0 else 0
                ),
                'cumulative_regret': self.metrics['cumulative_regret'],
                'avg_decision_time_ms': avg_decision_time,
                'last_decision': (
                    self.decisions[-1].__dict__ if self.decisions else None
                ),
                'initialized': True,
                'alpha': np.mean([arm.alpha for arm in self.arms.values()]),
                'beta': np.mean([arm.beta for arm in self.arms.values()])
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        with self.lock:
            if not self.metrics['start_time']:
                runtime_seconds = 0
            else:
                runtime_seconds = (datetime.now() - self.metrics['start_time']).total_seconds()
            
            return {
                'runtime_seconds': runtime_seconds,
                'total_decisions': self.metrics['total_decisions'],
                'total_reward': self.metrics['total_reward'],
                'cumulative_regret': self.metrics['cumulative_regret'],
                'decisions_per_second': (
                    self.metrics['total_decisions'] / runtime_seconds
                    if runtime_seconds > 0 else 0
                ),
                'avg_decision_time_ms': (
                    np.mean(self.metrics['decision_times_ms'])
                    if self.metrics['decision_times_ms'] else 0
                ),
                'p95_decision_time_ms': (
                    np.percentile(self.metrics['decision_times_ms'], 95)
                    if len(self.metrics['decision_times_ms']) > 0 else 0
                ),
                'arm_statistics': self.get_arm_statistics()
            }
    
    def start(self, interval_seconds: float = 1.0) -> bool:
        """Start the Governor in background thread"""
        with self.lock:
            if self.running:
                return False
            
            self.running = True
            self.metrics['start_time'] = datetime.now()
            
            def run():
                while self.running:
                    time.sleep(interval_seconds)
                    # In real implementation, would make decisions here
                    # For now, just maintain running state
            
            self.thread = threading.Thread(target=run, daemon=True)
            self.thread.start()
            
            print(f"[OK] Governor started in {self.mode} mode")
            return True
    
    def stop(self) -> bool:
        """Stop the Governor"""
        with self.lock:
            if not self.running:
                return False
            
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            
            print("[OK] Governor stopped")
            return True
    
    def set_mode(self, mode: str) -> bool:
        """Change Governor mode"""
        valid_modes = ['thompson_sampling', 'ucb', 'epsilon_greedy']
        if mode in valid_modes:
            with self.lock:
                self.mode = mode
                print(f"[OK] Governor mode changed to: {mode}")
                return True
        return False
    
    def reset_statistics(self):
        """Reset all statistics but keep arm configurations"""
        with self.lock:
            for arm in self.arms.values():
                arm.alpha = 1.0
                arm.beta = 1.0
                arm.pulls = 0
                arm.successes = 0
                arm.failures = 0
                arm.last_pull = None
            
            self.decisions.clear()
            self.metrics = {
                'total_decisions': 0,
                'total_reward': 0,
                'cumulative_regret': 0,
                'start_time': datetime.now() if self.running else None,
                'last_decision_time': None,
                'decision_times_ms': deque(maxlen=100)
            }
            
            print("[OK] Governor statistics reset")
    
    def export_state(self) -> str:
        """Export Governor state as JSON"""
        with self.lock:
            state = {
                'mode': self.mode,
                'arms': {
                    arm_id: {
                        'name': arm.name,
                        'alpha': arm.alpha,
                        'beta': arm.beta,
                        'pulls': arm.pulls,
                        'successes': arm.successes,
                        'failures': arm.failures,
                        'metadata': arm.metadata
                    }
                    for arm_id, arm in self.arms.items()
                },
                'metrics': {
                    'total_decisions': self.metrics['total_decisions'],
                    'total_reward': self.metrics['total_reward'],
                    'cumulative_regret': self.metrics['cumulative_regret']
                },
                'config': self.config
            }
            return json.dumps(state, indent=2)
    
    def import_state(self, state_json: str) -> bool:
        """Import Governor state from JSON"""
        try:
            state = json.loads(state_json)
            
            with self.lock:
                self.mode = state.get('mode', 'thompson_sampling')
                self.config.update(state.get('config', {}))
                
                # Restore arms
                self.arms.clear()
                for arm_id, arm_data in state.get('arms', {}).items():
                    arm = Arm(
                        id=arm_id,
                        name=arm_data['name'],
                        alpha=arm_data['alpha'],
                        beta=arm_data['beta'],
                        metadata=arm_data.get('metadata', {})
                    )
                    arm.pulls = arm_data['pulls']
                    arm.successes = arm_data['successes']
                    arm.failures = arm_data['failures']
                    self.arms[arm_id] = arm
                
                # Restore metrics
                metrics = state.get('metrics', {})
                self.metrics['total_decisions'] = metrics.get('total_decisions', 0)
                self.metrics['total_reward'] = metrics.get('total_reward', 0)
                self.metrics['cumulative_regret'] = metrics.get('cumulative_regret', 0)
                
                print("[OK] Governor state imported successfully")
                return True
                
        except Exception as e:
            print(f"[ERROR] Failed to import state: {e}")
            return False

# Singleton instance
_governor_instance = None

def get_optimized_governor() -> OptimizedGovernor:
    """Get or create the singleton Governor instance"""
    global _governor_instance
    if _governor_instance is None:
        _governor_instance = OptimizedGovernor()
    return _governor_instance

# For backward compatibility
def get_governor_adapter():
    """Backward compatible function"""
    return get_optimized_governor()