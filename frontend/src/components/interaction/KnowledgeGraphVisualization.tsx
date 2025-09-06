import React, { useRef, useEffect, useState } from 'react';
import { RefreshCw, Maximize2, Download, ZoomIn, ZoomOut } from 'lucide-react';

const KnowledgeGraphVisualization = () => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [graphUrl, setGraphUrl] = useState('/knowledge_graph.html');
  const [graphData, setGraphData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [autoUpdateEnabled, setAutoUpdateEnabled] = useState(true);
  const [updateInterval, setUpdateInterval] = useState(30); // seconds
  const [emergencyGeneratorStatus, setEmergencyGeneratorStatus] = useState<string>('unknown');

  useEffect(() => {
    // Load the visualization
    const loadVisualization = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // The graph HTML is served from public folder
        // Updated by kb_visualizer.py via the Governor
        setGraphUrl(`/knowledge_graph.html`);
        
        // Give iframe time to load
        setTimeout(() => {
          setIsLoading(false);
          setLastUpdate(new Date());
        }, 500);
      } catch (err) {
        setError('Failed to load knowledge graph visualization');
        setIsLoading(false);
      }
    };

    loadVisualization();
  }, []);

  // Enhanced: Auto-update functionality
  useEffect(() => {
    if (!autoUpdateEnabled) return;

    const interval = setInterval(() => {
      fetchGraphData();
    }, updateInterval * 1000);

    return () => clearInterval(interval);
  }, [autoUpdateEnabled, updateInterval]);

  // Enhanced: Check emergency generator status
  const checkEmergencyGeneratorStatus = async () => {
    try {
      const { httpClient } = await import('@/services/api');
      const response = await httpClient.get('/api/graph/emergency-status');
      if (response.status === 200) {
        const status = response.data;
        setEmergencyGeneratorStatus(status.status || 'unknown');
      }
    } catch (error) {
      console.warn('Could not check emergency generator status:', error);
    }
  };

  // Enhanced: Trigger emergency graph generation
  const triggerEmergencyGeneration = async () => {
    try {
      setLoading(true);
      const { httpClient } = await import('@/services/api');
      const response = await httpClient.post('/api/graph/emergency-generate');
      
      if (response.status === 200) {
        const result = response.data;
        if (result.success) {
          await fetchGraphData();
          setEmergencyGeneratorStatus('completed');
        } else {
          setEmergencyGeneratorStatus('failed');
        }
      }
    } catch (error) {
      console.error('Emergency generation failed:', error);
      setEmergencyGeneratorStatus('failed');
    } finally {
      setLoading(false);
    }
  };

  // Enhanced: Update graph configuration
  const updateGraphConfig = async (config: any) => {
    try {
      const { httpClient } = await import('@/services/api');
      const response = await httpClient.post('/api/graph/config', config);
      
      if (response.status === 200) {
        await fetchGraphData();
      }
    } catch (error) {
      console.error('Failed to update graph config:', error);
    }
  };

  const handleRefresh = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      
      // Call API to generate new graph
      const { httpClient } = await import('@/services/api');
      const { data: result } = await httpClient.post(`/api/graph/generate`);
      
      if (result.success) {
        // Graph generated successfully, now reload the iframe
        if (iframeRef.current) {
          // Force reload with cache bust
          const timestamp = new Date().getTime();
          iframeRef.current.src = '';
          setTimeout(() => {
            iframeRef.current!.src = `/knowledge_graph.html?t=${timestamp}`;
            setGraphUrl(`/knowledge_graph.html?t=${timestamp}`);
            setLastUpdate(new Date());
          }, 100);
        }
      } else {
        setError(result.error || 'Failed to generate graph');
      }
    } catch (err) {
      console.error('Error generating graph:', err);
      setError('Failed to generate graph. Is the backend running?');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleFullscreen = () => {
    if (iframeRef.current) {
      if (iframeRef.current.requestFullscreen) {
        iframeRef.current.requestFullscreen();
      }
    }
  };

  const handleZoomIn = () => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage({ action: 'zoom', direction: 'in' }, '*');
    }
  };

  const handleZoomOut = () => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage({ action: 'zoom', direction: 'out' }, '*');
    }
  };

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <span className="text-2xl">🧠</span>
            Neural Knowledge Network
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Interactive visualization of the HAK-GAL knowledge base
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            className="p-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <button
            onClick={handleZoomIn}
            className="p-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            onClick={handleFullscreen}
            className="p-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors"
            title="Fullscreen"
          >
            <Maximize2 className="h-4 w-4" />
          </button>
          <button
            onClick={handleRefresh}
            disabled={isGenerating}
            className={`
              p-2 rounded-md transition-colors
              ${isGenerating 
                ? 'bg-primary/20 text-primary cursor-not-allowed' 
                : 'hover:bg-accent hover:text-accent-foreground'
              }
            `}
            title={isGenerating ? "Generating graph..." : "Generate & Refresh Graph"}
          >
            <RefreshCw className={`h-4 w-4 ${isGenerating ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
      
      <div className="flex-1 relative">
        {(isLoading || isGenerating) && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-10">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-sm text-muted-foreground">
                {isGenerating ? 'Generating new graph...' : 'Loading neural network visualization...'}
              </p>
              {isGenerating && (
                <p className="text-xs text-muted-foreground mt-2">
                  This may take a few seconds depending on the knowledge base size
                </p>
              )}
            </div>
          </div>
        )}
        
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm z-10">
            <div className="text-center p-6">
              <div className="text-destructive text-4xl mb-2">⚠️</div>
              <p className="text-sm text-destructive">{error}</p>
              <button
                onClick={handleRefresh}
                className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
        
        <iframe
          ref={iframeRef}
          src={graphUrl}
          className="w-full h-full border-0"
          title="Knowledge Graph"
          onLoad={() => {
            if (!isGenerating) {
              setIsLoading(false);
              setError(null);
            }
          }}
          onError={() => {
            if (!isGenerating) {
              setError('Failed to load visualization. Click refresh to generate the graph.');
              setIsLoading(false);
            }
          }}
          style={{
            backgroundColor: '#000',
            minHeight: '100%'
          }}
        />
      </div>
      
      <div className="p-4 border-t border-border bg-muted/50">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#4A90E2]" />
                <span className="text-xs">Physics</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#4CAF50]" />
                <span className="text-xs">Biology</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#FF5722]" />
                <span className="text-xs">AI</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#673AB7]" />
                <span className="text-xs">Space</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#FFC107]" />
                <span className="text-xs">Energy</span>
              </div>
            </div>
            
            <div className="text-xs text-muted-foreground">
              Node size = Number of connections | Edge color = Relationship type
            </div>
          </div>
          
          <div className="text-xs text-muted-foreground">
            {isGenerating ? (
              <span className="text-primary">Generating graph...</span>
            ) : (
              `Last update: ${lastUpdate.toLocaleTimeString()}`
            )}
          </div>
        </div>
        
        <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
          <span>💡 Tip: Click refresh button to regenerate graph • Drag nodes to reorganize • Scroll to zoom</span>
          <a 
            href="/knowledge_growth.html" 
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline ml-auto"
          >
            View Growth Animation →
          </a>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraphVisualization;
