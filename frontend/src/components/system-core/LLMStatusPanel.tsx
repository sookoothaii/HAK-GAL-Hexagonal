import React from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';

const LLMStatusPanel = () => {
  const llmProviders = useGovernorStore(state => state.llmProviders);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-success';
      case 'offline': return 'text-muted-foreground';
      case 'error': return 'text-destructive';
      default: return 'text-muted-foreground';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return '●';
      case 'offline': return '○';
      case 'error': return '▲';
      default: return '○';
    }
  };

  // Enhanced: Better status determination from backend data
  const getEnhancedStatus = (llm: any) => {
    // Check if provider has token usage (indicates activity)
    if (llm.tokens_used > 0 || llm.tokensUsed > 0) {
      return 'online';
    }
    // Check for API errors
    if (llm.status === 'error' || llm.error) {
      return 'error';
    }
    // Check for specific provider status
    if (llm.status === 'online' || llm.active) {
      return 'online';
    }
    return 'offline';
  };

  // Enhanced: Get comprehensive metrics
  const getProviderMetrics = (llm: any) => {
    const tokensUsed = llm.tokens_used || llm.tokensUsed || 0;
    const cost = llm.cost || 0;
    const responseTime = llm.response_time || llm.responseTime || 0;
    const model = llm.model || 'Unknown';
    const name = llm.name || 'Unknown Provider';
    
    return {
      tokensUsed,
      cost,
      responseTime,
      model,
      name,
      status: getEnhancedStatus(llm)
    };
  };

  const totalCost = llmProviders.reduce((sum, llm) => sum + (llm.cost || 0), 0);
  const totalTokens = llmProviders.reduce((sum, llm) => sum + (llm.tokens_used || llm.tokensUsed || 0), 0);
  const activeProviders = llmProviders.filter(llm => getEnhancedStatus(llm) === 'online').length;

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold">LLM Status Panel</h2>
        <p className="text-xs text-muted-foreground">
          {activeProviders} of {llmProviders.length} providers active
        </p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {llmProviders.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm text-muted-foreground">
              No LLM providers connected. Waiting for data...
            </p>
          </div>
        ) : (
          llmProviders.map((llm, idx) => {
            const metrics = getProviderMetrics(llm);
            return (
              <div key={idx} className="p-3 rounded-lg bg-background border border-border neural-border">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-lg ${getStatusColor(metrics.status)}`}>
                      {getStatusIcon(metrics.status)}
                    </span>
                    <div>
                      <div className="font-medium">{metrics.name}</div>
                      <div className="text-xs text-muted-foreground">{metrics.model}</div>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    metrics.status === 'online' ? 'bg-success/20 text-success' : 
                    metrics.status === 'error' ? 'bg-destructive/20 text-destructive' : 
                    'bg-muted text-muted-foreground'
                  }`}>
                    {metrics.status.toUpperCase()}
                  </span>
                </div>
                
                {metrics.status === 'online' && (
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="text-muted-foreground">Tokens:</span>
                      <div className="font-mono">{metrics.tokensUsed.toLocaleString()}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Cost:</span>
                      <div className="font-mono">${metrics.cost.toFixed(2)}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Response:</span>
                      <div className="font-mono">{metrics.responseTime}ms</div>
                    </div>
                  </div>
                )}
                
                {/* Enhanced: Show additional backend data if available */}
                {llm.error && (
                  <div className="mt-2 p-2 bg-destructive/10 rounded text-xs text-destructive">
                    Error: {llm.error}
                  </div>
                )}
                
                {llm.last_used && (
                  <div className="mt-1 text-xs text-muted-foreground">
                    Last used: {new Date(llm.last_used).toLocaleTimeString()}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
      
      <div className="p-4 border-t border-border bg-muted/50">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Total Tokens:</span>
            <div className="font-mono font-semibold">{totalTokens.toLocaleString()}</div>
          </div>
          <div>
            <span className="text-muted-foreground">Total Cost:</span>
            <div className="font-mono font-semibold text-primary">${totalCost.toFixed(2)}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMStatusPanel;
