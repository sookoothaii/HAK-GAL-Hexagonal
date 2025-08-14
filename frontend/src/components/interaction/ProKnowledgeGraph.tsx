// V2 - Simplified iFrame Wrapper for Real-Time Visualization
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { RefreshCw, Loader2, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

const ProKnowledgeGraph: React.FC = () => {
  const [iframeKey, setIframeKey] = useState(Date.now());
  const [isLoading, setIsLoading] = useState(true);
  
  const lastVisualizationUrl = useGovernorStore(state => state.kb.last_visualization_url);
  const isConnected = useGovernorStore(state => state.isConnected);

  useEffect(() => {
    // When a new visualization is available from the backend, refresh the iframe
    if (lastVisualizationUrl) {
      console.log("New visualization available, refreshing iframe:", lastVisualizationUrl);
      setIsLoading(true);
      setIframeKey(Date.now()); // Change key to force iframe reload
      toast.success("Knowledge graph has been updated.");
    }
  }, [lastVisualizationUrl]);

  const handleRefresh = () => {
    setIsLoading(true);
    setIframeKey(Date.now());
  };

  const handleLoad = () => {
    setIsLoading(false);
  };

  if (!isConnected) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <AlertTriangle className="w-5 h-5 mr-2" /> Not Connected to Backend
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-4">
      <Card className="flex-1 flex flex-col border-0 bg-card/50">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Knowledge Graph Visualization</CardTitle>
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </CardHeader>
        <CardContent className="flex-1 relative">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/50 z-10">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          )}
          <iframe
            key={iframeKey}
            src="/knowledge_graph.html"
            title="Knowledge Graph"
            className="w-full h-full border-0 rounded-md"
            onLoad={handleLoad}
          />
        </CardContent>
      </Card>
    </div>
  );
};

export default ProKnowledgeGraph;