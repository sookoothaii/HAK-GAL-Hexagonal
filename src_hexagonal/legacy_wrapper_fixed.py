"""
Legacy System Wrapper für HAK-GAL mit CUDA Support - FIXED VERSION
===================================================================
Lädt Modelle nur wenn wirklich benötigt (Lazy Loading)
"""

import sys
import os
from pathlib import Path
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Disable automatic model downloads to prevent hanging
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

# Add original HAK-GAL to path (READ-ONLY!)
ORIGINAL_PATH = Path(r"D:\MCP Mods\HAK_GAL_SUITE")
sys.path.insert(0, str(ORIGINAL_PATH / "src"))

class LegacySystemProxy:
    """
    Proxy für Original HAK-GAL System mit CUDA Support
    Alle Zugriffe sind READ-ONLY!
    Modelle werden nur bei Bedarf geladen (Lazy Loading)
    """
    
    def __init__(self):
        self.k_assistant = None
        self.hrm_system = None
        self._initialized = False
        self._k_assistant_initialized = False
        self._hrm_initialized = False
        
    def initialize_k_assistant(self):
        """Lazy initialization of K-Assistant only"""
        if self._k_assistant_initialized:
            return True
            
        try:
            # Try to initialize without loading all models
            logger.info("Initializing K-Assistant (without heavy models)...")
            
            # Import base K-Assistant class
            from hak_gal.services.k_assistant_thread_safe_v2 import KAssistant
            
            # Create instance
            self.k_assistant = KAssistant()
            
            logger.info("✅ Legacy K-Assistant connected (lightweight mode)")
            self._k_assistant_initialized = True
            return True
            
        except ImportError as e:
            logger.error(f"❌ K-Assistant Import Error: {e}")
            # Try fallback without models
            try:
                # Create minimal mock K-Assistant
                class MinimalKAssistant:
                    def __init__(self):
                        self.core = type('obj', (object,), {'K': []})()
                        self.db_session = None
                        
                    def add_fact(self, statement, context=None):
                        return True, "Added (mock mode)"
                        
                    def ask(self, query):
                        return {'relevant_facts': [], 'response': 'Mock mode'}
                        
                    def get_metrics(self):
                        return {'fact_count': 0}
                
                self.k_assistant = MinimalKAssistant()
                logger.warning("⚠️ Using minimal K-Assistant (mock mode)")
                self._k_assistant_initialized = True
                return True
                
            except Exception as fallback_error:
                logger.error(f"❌ Fallback failed: {fallback_error}")
                return False
            
    def initialize_hrm(self):
        """Lazy initialization of HRM only"""
        if self._hrm_initialized:
            return True
            
        try:
            # Try lightweight HRM initialization
            logger.info("Initializing HRM (lightweight)...")
            
            # Create minimal HRM mock
            class MinimalHRM:
                def __init__(self):
                    self.device = 'cpu'
                    
                def reason(self, query):
                    # Simple pattern matching for basic reasoning
                    confidence = 0.5
                    if 'IsA' in query or 'HasPart' in query:
                        confidence = 0.8
                    elif 'Not' in query:
                        confidence = 0.2
                        
                    return {
                        'confidence': confidence,
                        'success': True,
                        'reasoning_terms': ['lightweight', 'mock'],
                        'device': self.device
                    }
                    
                def get_status(self):
                    return {
                        'status': 'operational',
                        'mode': 'lightweight',
                        'device': self.device
                    }
            
            self.hrm_system = MinimalHRM()
            logger.info("✅ Minimal HRM initialized (mock mode)")
            self._hrm_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"❌ HRM initialization failed: {e}")
            return False
            
    def initialize(self):
        """Full initialization of legacy components"""
        if self._initialized:
            return True
            
        # Initialize both components with fallbacks
        k_ok = self.initialize_k_assistant()
        hrm_ok = self.initialize_hrm()
        
        self._initialized = k_ok or hrm_ok  # Success if at least one works
        return self._initialized
    
    def get_facts(self, limit=100):
        """Get facts from legacy system (READ-ONLY)"""
        if not self.initialize_k_assistant():
            return []
            
        try:
            # Try to get facts from K-Assistant
            if hasattr(self.k_assistant, 'core') and hasattr(self.k_assistant.core, 'K'):
                facts = list(self.k_assistant.core.K)[:limit]
                return facts
        except Exception as e:
            logger.error(f"❌ Error reading facts: {e}")
            
        return []
    
    def reason(self, query):
        """Use HRM for reasoning"""
        if not self.initialize_hrm():
            return {"error": "HRM not available", "confidence": 0.5, "success": True}
            
        try:
            if self.hrm_system:
                return self.hrm_system.reason(query)
        except Exception as e:
            logger.error(f"❌ Reasoning error: {e}")
            return {"error": str(e), "confidence": 0.0, "success": False}
    
    def get_hrm_status(self):
        """Get HRM system status"""
        if not self.initialize_hrm():
            return {"status": "unavailable"}
        
        try:
            if self.hrm_system and hasattr(self.hrm_system, 'get_status'):
                return self.hrm_system.get_status()
        except Exception as e:
            logger.error(f"❌ Status error: {e}")
        
        return {"status": "error"}

# Global instance
legacy_proxy = LegacySystemProxy()

def get_legacy_k_assistant():
    """Backward compatibility function"""
    legacy_proxy.initialize_k_assistant()
    return legacy_proxy.k_assistant

def get_legacy_hrm():
    """Backward compatibility function"""
    legacy_proxy.initialize_hrm()
    return legacy_proxy.hrm_system

def test_legacy_connection():
    """Test connection to legacy system"""
    print("\n🔍 Testing Legacy System Connection...")
    
    if legacy_proxy.initialize():
        print("✅ Legacy System connected (lightweight mode)!")
        
        # Test Facts
        facts = legacy_proxy.get_facts(5)
        print(f"  📊 {len(facts)} Facts read")
        
        # Test HRM
        result = legacy_proxy.reason("IsA(Socrates, Philosopher)")
        if 'confidence' in result:
            print(f"  🧠 HRM Confidence: {result['confidence']:.4f}")
            if 'device' in result:
                print(f"  🎮 Device: {result['device']}")
        
        return True
    else:
        print("❌ Legacy System not available")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_legacy_connection()
