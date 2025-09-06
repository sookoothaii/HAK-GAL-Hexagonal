# LLM Configuration API Integration
# Add this to your hexagonal_api_enhanced_clean.py

from flask import request, jsonify
import json
import os

# Store configuration in memory (or use Redis/DB for persistence)
llm_config_store = {
    'providers': {},
    'enabled_providers': ['groq', 'deepseek', 'gemini', 'claude', 'ollama'],
    'provider_order': ['groq', 'deepseek', 'gemini', 'claude', 'ollama'],
    'api_keys': {}
}

# Load configuration from file on startup
try:
    with open('llm_config.json', 'r') as f:
        saved_config = json.load(f)
        llm_config_store.update(saved_config)
        print(f"[LLM Config] Loaded configuration from llm_config.json")
except Exception as e:
    print(f"[LLM Config] No saved configuration found: {e}")

def init_llm_config_routes(app):
    """Initialize LLM configuration routes"""
    
    @app.route('/api/llm/config', methods=['GET', 'POST'])
    def handle_llm_config():
        global llm_config_store
        
        if request.method == 'GET':
            # Return current configuration
            return jsonify(llm_config_store)
        
        elif request.method == 'POST':
            data = request.json
            
            # Update configuration
            providers = data.get('providers', [])
            enabled = []
            order = []
            api_keys = {}
            
            for p in sorted(providers, key=lambda x: x.get('order', 999)):
                provider_id = p['id']
                order.append(provider_id)
                
                if p.get('enabled'):
                    enabled.append(provider_id)
                
                if p.get('tempApiKey'):
                    api_keys[provider_id] = p['tempApiKey']
            
            llm_config_store = {
                'providers': {p['id']: p for p in providers},
                'enabled_providers': enabled,
                'provider_order': order,
                'api_keys': api_keys
            }
            
            # Update the actual LLM provider chain
            update_provider_chain()
            
            
            # Also save configuration to file for MultiLLMProvider
            import json
            config_file = {
                'enabled_providers': enabled,
                'provider_order': order,
                'api_keys': api_keys
            }
            
            try:
                with open('llm_config.json', 'w') as f:
                    json.dump(config_file, f, indent=2)
                print(f"[LLM Config] Saved configuration to llm_config.json")
            except Exception as e:
                print(f"[LLM Config] Failed to save config file: {e}")
            
            return jsonify({'success': True})
    
    @app.route('/api/llm/test', methods=['POST'])
    def test_llm_provider():
        """Test a specific LLM provider"""
        data = request.json
        provider_id = data.get('provider')
        temp_key = data.get('apiKey')
        
        # Import providers
        from src_hexagonal.adapters.llm_providers import (
            GroqProvider, DeepSeekProvider, GeminiProvider, 
            ClaudeProvider, OllamaProvider
        )
        
        # Map provider IDs to classes
        provider_map = {
            'groq': GroqProvider,
            'deepseek': DeepSeekProvider,
            'gemini': GeminiProvider,
            'claude': ClaudeProvider,
            'ollama': OllamaProvider
        }
        
        if provider_id not in provider_map:
            return jsonify({'success': False, 'error': 'Unknown provider'})
        
        # Create provider instance
        provider_class = provider_map[provider_id]
        provider = provider_class()
        
        # Temporarily override API key if provided
        if temp_key and hasattr(provider, 'api_key'):
            old_key = provider.api_key
            provider.api_key = temp_key
        
        try:
            # Test availability
            if not provider.is_available():
                return jsonify({
                    'success': False, 
                    'error': 'Provider not available (check API key)'
                })
            
            # Test with simple prompt
            test_prompt = "Say 'Hello' in one word"
            response, _ = provider.generate_response(test_prompt)
            
            if response and len(response) > 0:
                return jsonify({
                    'success': True,
                    'response': response[:100]
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Empty response'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })
        finally:
            # Restore original key
            if temp_key and hasattr(provider, 'api_key'):
                provider.api_key = old_key
    
    @app.route('/api/llm/check-env-keys', methods=['GET'])
    def check_env_keys():
        """Check which providers have environment keys set"""
        return jsonify({
            'groq': bool(os.environ.get('GROQ_API_KEY')),
            'deepseek': bool(os.environ.get('DEEPSEEK_API_KEY')),
            'gemini': bool(os.environ.get('GEMINI_API_KEY')),
            'claude': bool(os.environ.get('ANTHROPIC_API_KEY')),
            'ollama': True  # Always true for local
        })
    
    @app.route('/api/llm/update-chain', methods=['POST'])
    def update_provider_chain():
        """Update the active provider chain based on configuration"""
        # This would update the MultiLLMProvider instance
        # to use only enabled providers in the specified order
        
        # For now, just log the change
        print(f"[LLM Config] Updated provider chain:")
        print(f"  Enabled: {llm_config_store['enabled_providers']}")
        print(f"  Order: {llm_config_store['provider_order']}")
        
        return jsonify({'success': True})

# Add this to your main app initialization:
# init_llm_config_routes(app)
