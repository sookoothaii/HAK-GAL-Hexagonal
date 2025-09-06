// ProUnifiedQueryEnhanced.tsx - With Confidence Learning
// ========================================================
// Enhanced version with confidence cache and HRM feedback integration

import React from 'react';
import { toast } from 'sonner';
import { useConfidenceCache } from '@/hooks/useConfidenceCache';
import { getActiveBackend } from '@/config/backends';

// Import original component
import UnifiedQueryInterface from './ProUnifiedQuery';

/**
 * Integration wrapper for ProUnifiedQuery with Confidence Learning
 * This patches the existing component with learning capabilities
 */
export const patchQueryInterfaceWithLearning = () => {
  const { getAdjustedConfidence, addVerification, getStatistics } = useConfidenceCache();
  const activeBackend = getActiveBackend();
  const baseUrl = activeBackend.apiUrl;
  
  // Monkey-patch the window object to intercept HRM calls
  if (typeof window !== 'undefined' && !(window as any).__hrmLearningPatched) {
    const originalFetch = window.fetch;
    
    window.fetch = async function(...args) {
      const [url, options] = args;
      
      // Intercept HRM reason calls
      if (typeof url === 'string' && url.includes('/api/reason')) {
        const response = await originalFetch.apply(this, args);
        
        // Clone response to read it
        const cloned = response.clone();
        
        try {
          const data = await cloned.json();
          
          if (data && data.query && typeof data.confidence === 'number') {
            // Get adjusted confidence from cache
            const adjusted = getAdjustedConfidence(data.query, data.confidence);
            
            // If we have history, send feedback to backend
            if (adjusted.hasHistory && adjusted.feedbackCount > 0) {
              // Fire and forget - don't wait for response
              originalFetch(`${baseUrl}/api/hrm/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  query: data.query,
                  type: 'positive', // Default to positive for existing verifications
                  confidence: data.confidence
                })
              }).catch(err => console.error('Failed to send HRM feedback:', err));
            }
            
            // Return modified response with adjusted confidence
            const modifiedData = {
              ...data,
              original_confidence: data.confidence,
              confidence: adjusted.confidence,
              has_learning_history: adjusted.hasHistory,
              feedback_count: adjusted.feedbackCount,
              confidence_adjustment: adjusted.adjustment
            };
            
            // Create new response with modified data
            return new Response(JSON.stringify(modifiedData), {
              status: response.status,
              statusText: response.statusText,
              headers: response.headers
            });
          }
        } catch (e) {
          // If parsing fails, return original response
          console.error('Failed to enhance HRM response:', e);
        }
        
        return response;
      }
      
      // For all other requests, use original fetch
      return originalFetch.apply(this, args);
    };
    
    (window as any).__hrmLearningPatched = true;
    console.log('✅ HRM Learning patch applied');
  }
  
  // Also patch the verify button behavior
  const originalVerifyHandler = (window as any).__originalVerifyHandler;
  if (!originalVerifyHandler) {
    // Store original handler
    (window as any).__originalVerifyHandler = true;
    
    // Add global event listener for verify buttons
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      
      // Check if it's a verify button
      if (target.textContent?.includes('Verify Response') || 
          target.closest('button')?.textContent?.includes('Verify Response')) {
        
        // Find the query from parent elements
        const card = target.closest('[data-query]');
        if (card) {
          const query = card.getAttribute('data-query');
          const confidence = parseFloat(card.getAttribute('data-confidence') || '0.5');
          
          if (query) {
            // Add positive verification to cache
            addVerification(query, 'positive', confidence);
            
            // Send to backend
            fetch(`${baseUrl}/api/hrm/feedback`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                query: query,
                type: 'positive',
                confidence: confidence
              })
            }).then(response => {
              if (response.ok) {
                toast.success('Learning feedback recorded - confidence will improve with more verifications');
              }
            }).catch(err => {
              console.error('Failed to send feedback:', err);
            });
          }
        }
      }
    });
  }
  
  // Return stats for debugging
  return {
    stats: getStatistics(),
    addVerification,
    getAdjustedConfidence
  };
};

/**
 * Enhanced Query Interface with Learning
 */
const EnhancedUnifiedQueryInterface: React.FC = () => {
  // Apply learning patch
  React.useEffect(() => {
    const learning = patchQueryInterfaceWithLearning();
    console.log('Confidence Learning Stats:', learning.stats);
    
    // Add data attributes to cards for event handler
    const interval = setInterval(() => {
      document.querySelectorAll('.trust-score-card').forEach(card => {
        const parent = card.closest('[data-query-result]');
        if (parent) {
          const query = parent.getAttribute('data-query');
          const confidence = parent.getAttribute('data-confidence');
          if (query && confidence) {
            card.setAttribute('data-query', query);
            card.setAttribute('data-confidence', confidence);
          }
        }
      });
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Render original component
  return <UnifiedQueryInterface />;
};

export default EnhancedUnifiedQueryInterface;
