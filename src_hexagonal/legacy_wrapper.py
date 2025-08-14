"""
Legacy System Wrapper für HAK-GAL mit CUDA Support
===================================================
Ermöglicht sicheren Read-Only Zugriff auf Original HAK-GAL
ohne das System zu modifizieren.

Nach HAK/GAL Verfassung Artikel 3: Externe Verifikation
"""

import sys
from pathlib import Path
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Add original HAK-GAL to path (READ-ONLY!)
ORIGINAL_PATH = Path(r"D:\MCP Mods\HAK_GAL_SUITE")
sys.path.insert(0, str(ORIGINAL_PATH / "src"))

class LegacySystemProxy:
    """
    Proxy für Original HAK-GAL System mit CUDA Support
    Alle Zugriffe sind READ-ONLY!
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
            # Import K-Assistant Klasse
            from hak_gal.services.k_assistant_thread_safe_v2 import KAssistant
            # Erstelle neue Instanz oder hole existierende
            if not self.k_assistant:
                self.k_assistant = KAssistant()
            logger.info("✅ Legacy K-Assistant verbunden")
            self._k_assistant_initialized = True
            return True
        except ImportError as e:
            logger.error(f"❌ K-Assistant Import Fehler: {e}")
            return False
            
    def initialize_hrm(self):
        """Lazy initialization of HRM only"""
        if self._hrm_initialized:
            return True
            
        try:
            # Import HRM with CUDA support
            sys.path.insert(0, str(ORIGINAL_PATH / "hrm_unified"))
            from unified_hrm_api import get_hrm_instance
            self.hrm_system = get_hrm_instance()
            
            # Check if CUDA is active
            if hasattr(self.hrm_system, 'device'):
                if self.hrm_system.device.startswith('cuda'):
                    logger.info(f"✅ Legacy HRM System verbunden mit CUDA: {self.hrm_system.device}")
                else:
                    logger.info(f"✅ Legacy HRM System verbunden auf: {self.hrm_system.device}")
            else:
                logger.info("✅ Legacy HRM System verbunden")
            
            self._hrm_initialized = True
            return True
            
        except ImportError as e:
            logger.error(f"❌ HRM Import Fehler: {e}")
            return False
            
    def initialize(self):
        """Full initialization of legacy components"""
        if self._initialized:
            return True
            
        # Initialize both components
        k_ok = self.initialize_k_assistant()
        hrm_ok = self.initialize_hrm()
        
        self._initialized = k_ok and hrm_ok
        return self._initialized
    
    def get_facts(self, limit=100):
        """Get facts from legacy system (READ-ONLY)"""
        if not self.initialize_k_assistant():  # Only need K-Assistant for facts
            return []
            
        try:
            # Use legacy K-Assistant's method
            if hasattr(self.k_assistant, 'core') and hasattr(self.k_assistant.core, 'K'):
                facts = list(self.k_assistant.core.K)[:limit]
                return facts
        except Exception as e:
            logger.error(f"❌ Fehler beim Lesen der Facts: {e}")
            
        return []
    
    def reason(self, query):
        """Use legacy HRM for reasoning with CUDA acceleration"""
        if not self.initialize_hrm():  # Only need HRM for reasoning
            return {"error": "Legacy system not available"}
            
        try:
            if self.hrm_system:
                result = self.hrm_system.reason(query)
                # Add device info if available
                if hasattr(self.hrm_system, 'device'):
                    result['device'] = str(self.hrm_system.device)
                return result
        except Exception as e:
            logger.error(f"❌ Reasoning Fehler: {e}")
            return {"error": str(e)}
    
    def get_hrm_status(self):
        """Get HRM system status including CUDA info"""
        if not self.initialize_hrm():  # Only need HRM for status
            return {"error": "Legacy system not available"}
        
        try:
            if self.hrm_system and hasattr(self.hrm_system, 'get_status'):
                return self.hrm_system.get_status()
        except Exception as e:
            logger.error(f"❌ Status Fehler: {e}")
        
        return {"error": "Status not available"}

# Global instance
legacy_proxy = LegacySystemProxy()

def get_legacy_k_assistant():
    """Backward compatibility function"""
    if legacy_proxy.initialize():
        return legacy_proxy.k_assistant
    # Fallback: Direkt instantiieren
    from hak_gal.services.k_assistant_thread_safe_v2 import KAssistant
    return KAssistant()

def get_legacy_hrm():
    """Backward compatibility function"""
    legacy_proxy.initialize()
    return legacy_proxy.hrm_system

def test_legacy_connection():
    """Test ob Verbindung zum Legacy System funktioniert"""
    print("\n🔍 Teste Legacy System Verbindung...")
    
    if legacy_proxy.initialize():
        print("✅ Legacy System erfolgreich verbunden!")
        
        # Test Facts
        facts = legacy_proxy.get_facts(5)
        print(f"  📊 {len(facts)} Facts gelesen")
        
        # Test HRM with device info
        result = legacy_proxy.reason("HasTrait(Mammalia,ProducesMilk)")
        if 'confidence' in result:
            print(f"  🧠 HRM Confidence: {result['confidence']:.4f}")
            if 'device' in result:
                print(f"  🎮 Device: {result['device']}")
        
        # Get HRM status
        status = legacy_proxy.get_hrm_status()
        if 'cuda' in status and status['cuda'].get('available'):
            print(f"  ✅ CUDA Active: {status['cuda']['device_name']}")
        elif 'device' in status:
            print(f"  💻 Running on: {status['device']}")
        
        return True
    else:
        print("❌ Legacy System nicht verfügbar")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_legacy_connection()
