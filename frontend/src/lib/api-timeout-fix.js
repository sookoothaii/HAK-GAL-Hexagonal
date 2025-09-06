// Frontend Timeout Fix für HAK_GAL
// Fügen Sie diese Änderung in Ihre API-Konfiguration ein

// Option 1: Wenn Sie axios verwenden
const apiClient = axios.create({
  baseURL: 'http://localhost:5002',
  timeout: 60000, // 60 Sekunden statt 30
  headers: {
    'Content-Type': 'application/json'
  }
});

// Option 2: Wenn Sie fetch verwenden
const apiCall = async (url, options = {}) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 Sekunden
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

// Option 3: Spezifisch für LLM-Calls
const llmApiCall = async (endpoint, data) => {
  try {
    // Zeige Loading-Indicator
    console.log('LLM processing... This may take up to 60 seconds');
    
    const response = await fetch(`http://localhost:5002${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      signal: AbortSignal.timeout(60000) // 60 Sekunden
    });
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
    
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('Request timed out after 60 seconds');
      // Optional: Retry with delegate_task
      return { error: 'Timeout - try using simpler prompts or delegate_task' };
    }
    throw error;
  }
};

// Export für Verwendung
export { apiClient, apiCall, llmApiCall };
