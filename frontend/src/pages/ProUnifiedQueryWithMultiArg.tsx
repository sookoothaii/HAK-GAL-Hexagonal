// ProUnifiedQueryWithMultiArg.tsx
// Enhanced Query Interface with Multi-Argument Fact Generator
// ==============================================================

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import { Brain, Sparkles, Database, Search } from 'lucide-react';
import ProUnifiedQuery from './ProUnifiedQuery';
import MultiArgFactGenerator from '@/components/facts/MultiArgFactGenerator';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

export default function ProUnifiedQueryWithMultiArg() {
  const [activeTab, setActiveTab] = useState('query');
  const [factCount, setFactCount] = useState<number | null>(null);
  
  // Fetch fact count on mount
  React.useEffect(() => {
    fetchFactCount();
  }, []);
  
  const fetchFactCount = async () => {
    try {
      const response = await fetch('/api/facts/count');
      if (response.ok) {
        const data = await response.json();
        setFactCount(data.count);
      }
    } catch (error) {
      console.error('Failed to fetch fact count:', error);
    }
  };
  
  // Refresh count when switching tabs
  React.useEffect(() => {
    if (activeTab === 'generator') {
      fetchFactCount();
    }
  }, [activeTab]);
  
  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Brain className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold">Unified Intelligence Query</h1>
          {factCount !== null && (
            <Badge variant="secondary" className="ml-2">
              <Database className="w-3 h-3 mr-1" />
              {factCount} facts
            </Badge>
          )}
        </div>
      </div>
      
      {/* Tab Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="query" className="flex items-center gap-2">
            <Search className="w-4 h-4" />
            Query & Reasoning
          </TabsTrigger>
          <TabsTrigger value="generator" className="flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            Multi-Arg Generator
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="query" className="mt-6">
          <ProUnifiedQuery />
        </TabsContent>
        
        <TabsContent value="generator" className="mt-6">
          <div className="space-y-4">
            {/* Info Card */}
            <Card className="p-4 bg-muted/50">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-primary mt-0.5" />
                <div className="space-y-1">
                  <h3 className="font-semibold">Advanced Fact Generation</h3>
                  <p className="text-sm text-muted-foreground">
                    Generate complex facts with 3-7 arguments to enrich the knowledge base.
                    The backend now supports multi-argument predicates for more detailed knowledge representation.
                  </p>
                  <div className="flex gap-2 mt-2">
                    <Badge variant="outline">3 args: Moderate</Badge>
                    <Badge variant="outline">4-5 args: Complex</Badge>
                    <Badge variant="outline">6-7 args: Expert</Badge>
                  </div>
                </div>
              </div>
            </Card>
            
            {/* Multi-Arg Generator Component */}
            <MultiArgFactGenerator />
            
            {/* Stats Card */}
            <Card className="p-4">
              <h3 className="font-semibold mb-2">Generation Tips</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Use random examples to quickly generate diverse facts</li>
                <li>• Higher argument counts capture more detailed relationships</li>
                <li>• Facts are automatically validated for uniqueness</li>
                <li>• All facts include confidence scores and domain tags</li>
              </ul>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
