#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PATCH FILE: Integrate LLM Governor into hexagonal_api_enhanced_clean.py

HOW TO APPLY:
1. Add this import after other adapter imports (around line 92):
   from src_hexagonal.llm_governor_integration import integrate_llm_governor

2. Add initialization in __init__ method after governor init (around line 208):
   # Initialize LLM Governor
   self.llm_governor_integration = None
   if enable_governor:
       try:
           self.llm_governor_integration = integrate_llm_governor(self.app)
           print("[OK] LLM Governor Integration enabled")
       except Exception as e:
           print(f"[WARNING] LLM Governor Integration failed: {e}")

3. Update governor start/stop methods to use LLM Governor (around line 1740):
   @self.app.route('/api/governor/start', methods=['POST'])
   def governor_start():
       data = request.get_json(silent=True) or {}
       use_llm = data.get('use_llm', False)
       
       if use_llm and self.llm_governor_integration:
           self.llm_governor_integration.enabled = True
           return jsonify({'success': True, 'mode': 'llm_governor'})
       else:
           success = self.governor.start()
           return jsonify({'success': success, 'mode': 'thompson'})

4. Add status info for LLM Governor (in status route, around line 950):
   if self.llm_governor_integration:
       base_status['llm_governor'] = {
           'available': True,
           'enabled': self.llm_governor_integration.enabled,
           'provider': self.llm_governor_integration.config['provider'],
           'metrics': self.llm_governor_integration.get_metrics()
       }

That's it! The LLM Governor will be integrated.
"""

# COMPLETE MODIFIED SECTION FOR COPY-PASTE:
# This shows the exact code to add/modify

IMPORT_SECTION = """
# Add after line 92 (after other adapter imports):
from src_hexagonal.llm_governor_integration import integrate_llm_governor
"""

INIT_SECTION = """
# Add in __init__ method after line 208 (after self.governor init):
        # Initialize LLM Governor
        self.llm_governor_integration = None
        if enable_governor:
            try:
                self.llm_governor_integration = integrate_llm_governor(self.app)
                print("[OK] LLM Governor Integration enabled")
            except Exception as e:
                print(f"[WARNING] LLM Governor Integration failed: {e}")
"""

GOVERNOR_START_SECTION = """
# Replace governor_start method (around line 1740):
        @self.app.route('/api/governor/start', methods=['POST'])
        # @require_api_key
        def governor_start():
            data = request.get_json(silent=True) or {}
            use_llm = data.get('use_llm', False)
            
            # Check if LLM Governor requested
            if use_llm and self.llm_governor_integration:
                self.llm_governor_integration.enabled = True
                # Also start the standard governor for engines
                if self.governor:
                    self.governor.start()
                return jsonify({
                    'success': True, 
                    'mode': 'llm_governor',
                    'provider': self.llm_governor_integration.config['provider']
                })
            else:
                # Use standard Thompson governor
                success = self.governor.start() if self.governor else False
                return jsonify({'success': success, 'mode': 'thompson'})
"""

GOVERNOR_STOP_SECTION = """
# Replace governor_stop method:
        @self.app.route('/api/governor/stop', methods=['POST'])
        # @require_api_key
        def governor_stop():
            # Stop both governors
            success = False
            
            if self.llm_governor_integration:
                self.llm_governor_integration.enabled = False
                
            if self.governor:
                success = self.governor.stop()
                
            return jsonify({'success': success})
"""

STATUS_SECTION = """
# Add to status() method after governor status (around line 950):
            if self.llm_governor_integration:
                base_status['llm_governor'] = {
                    'available': True,
                    'enabled': self.llm_governor_integration.enabled,
                    'provider': self.llm_governor_integration.config['provider'],
                    'epsilon': self.llm_governor_integration.config['epsilon'],
                    'metrics': self.llm_governor_integration.get_metrics()
                }
"""

# TESTING THE INTEGRATION:
TEST_COMMANDS = """
# After applying the patch:

1. Restart the backend:
   Ctrl+C
   python src_hexagonal/hexagonal_api_enhanced_clean.py

2. Check LLM Governor status:
   curl http://localhost:5002/api/llm-governor/status

3. Enable LLM Governor:
   curl -X POST http://localhost:5002/api/llm-governor/enable \
        -H "Content-Type: application/json" \
        -d '{"provider": "groq", "epsilon": 0.2}'

4. Test from Frontend:
   - Click "Start Governor" 
   - Enable "Use LLM Governor" checkbox
   - Watch the console for LLM evaluations

5. Monitor metrics:
   curl http://localhost:5002/api/llm-governor/metrics
"""

if __name__ == "__main__":
    print("=" * 60)
    print("LLM GOVERNOR INTEGRATION PATCH")
    print("=" * 60)
    print("\nThis file contains the patches needed to integrate")
    print("the LLM Governor into hexagonal_api_enhanced_clean.py")
    print("\nFollow the instructions in the docstring above.")
    print("\nKey changes:")
    print("1. Import llm_governor_integration module")
    print("2. Initialize in __init__")
    print("3. Modify governor start/stop routes")
    print("4. Add status info")
    print("\nThe LLM Governor will then be available at:")
    print("- /api/llm-governor/status")
    print("- /api/llm-governor/enable")
    print("- /api/llm-governor/evaluate")
    print("- /api/llm-governor/metrics")
