import React, { useState } from 'react';
import KnowledgeGraphVisualization from '@/components/interaction/KnowledgeGraphVisualization';
import { ScalableKnowledgeBase } from '@/components/ScalableKnowledgeBase';
import { KnowledgeBaseFallback } from '@/components/KnowledgeBaseFallback';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Database, Network, List } from 'lucide-react';

const KnowledgePage = () => {
  const [activeTab, setActiveTab] = useState('list');
  
  // Check if react-window is available
  const hasReactWindow = typeof window !== 'undefined' && 'ResizeObserver' in window;
  
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <h1 className="text-2xl font-bold">Knowledge Base</h1>
        <p className="text-muted-foreground">
          Browse and search through the HAK-GAL knowledge base
        </p>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="mx-4 mt-4 w-fit">
          <TabsTrigger value="list" className="flex items-center gap-2">
            <List className="h-4 w-4" />
            List View
          </TabsTrigger>
          <TabsTrigger value="graph" className="flex items-center gap-2">
            <Network className="h-4 w-4" />
            Graph View
          </TabsTrigger>
          <TabsTrigger value="stats" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Statistics
          </TabsTrigger>
        </TabsList>
        
        <div className="flex-1 overflow-hidden">
          <TabsContent value="list" className="h-full mt-0">
            {hasReactWindow ? (
              <ScalableKnowledgeBase />
            ) : (
              <KnowledgeBaseFallback />
            )}
          </TabsContent>
          
          <TabsContent value="graph" className="h-full mt-0">
            <KnowledgeGraphVisualization />
          </TabsContent>
          
          <TabsContent value="stats" className="h-full mt-0 p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Total Facts</CardTitle>
                  <CardDescription>Number of facts in the knowledge base</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">6,121</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Database Size</CardTitle>
                  <CardDescription>Current database storage</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">0.89 MB</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Query Performance</CardTitle>
                  <CardDescription>Average query response time</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">0.4 ms</div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default KnowledgePage;
