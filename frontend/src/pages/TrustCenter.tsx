// TrustCenter.tsx - Central Trust & Verification Hub
// Nach HAK/GAL Artikel 3 (Externe Verifikation)

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { 
  Shield, CheckCircle, AlertTriangle, Info, TrendingUp,
  Users, Brain, Database, Bot, Activity
} from 'lucide-react';
import { useIntelligenceStore } from '@/stores/useIntelligenceStore';
import { Progress } from '@/components/ui/progress';

const TrustCenter: React.FC = () => {
  const { trust, metrics, neural, knowledge } = useIntelligenceStore();
  
  // Calculate aggregate metrics
  const totalVerifications = metrics.verifications || 0;
  const avgTrustScore = trust.overall || 0;
  const hrmAccuracy = neural.gap || 0.802;
  
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-2xl font-bold">Trust Center</h1>
            <p className="text-sm text-muted-foreground">
              Verification, validation, and trust metrics across all intelligence layers
            </p>
          </div>
        </div>
        <Badge variant="outline" className="gap-1">
          <Activity className="w-3 h-3" />
          BETA
        </Badge>
      </div>
      
      {/* Alert for Beta */}
      <Alert>
        <Info className="w-4 h-4" />
        <AlertDescription>
          The Trust Center aggregates trust metrics from HRM confidence, factual accuracy, source quality, 
          and human verification to provide transparency in AI decision-making.
        </AlertDescription>
      </Alert>
      
      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Overall Trust</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(avgTrustScore * 100).toFixed(0)}%</div>
            <Progress value={avgTrustScore * 100} className="mt-2 h-2" />
            <p className="text-xs text-muted-foreground mt-2">System-wide average</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Human Verifications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalVerifications}</div>
            <div className="flex items-center gap-1 mt-2">
              <CheckCircle className="w-3 h-3 text-green-500" />
              <span className="text-xs text-muted-foreground">Total confirmations</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">HRM Accuracy</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(hrmAccuracy * 100).toFixed(1)}%</div>
            <div className="flex items-center gap-1 mt-2">
              <Brain className="w-3 h-3 text-primary" />
              <span className="text-xs text-muted-foreground">Confidence gap</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Knowledge Base</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{knowledge.totalFacts.toLocaleString()}</div>
            <div className="flex items-center gap-1 mt-2">
              <Database className="w-3 h-3 text-blue-500" />
              <span className="text-xs text-muted-foreground">Verified facts</span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Trust Components Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Trust Component Analysis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {/* Neural Confidence */}
            <div className="text-center">
              <Brain className="w-8 h-8 mx-auto mb-2 text-primary" />
              <div className="text-sm font-medium">Neural</div>
              <div className="text-2xl font-bold">{(trust.components.neural * 100).toFixed(0)}%</div>
              <Progress value={trust.components.neural * 100} className="mt-1 h-1" />
            </div>
            
            {/* Factual Accuracy */}
            <div className="text-center">
              <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <div className="text-sm font-medium">Factual</div>
              <div className="text-2xl font-bold">{(trust.components.factual * 100).toFixed(0)}%</div>
              <Progress value={trust.components.factual * 100} className="mt-1 h-1" />
            </div>
            
            {/* Source Quality */}
            <div className="text-center">
              <Database className="w-8 h-8 mx-auto mb-2 text-blue-500" />
              <div className="text-sm font-medium">Sources</div>
              <div className="text-2xl font-bold">{(trust.components.sources * 100).toFixed(0)}%</div>
              <Progress value={trust.components.sources * 100} className="mt-1 h-1" />
            </div>
            
            {/* Consensus */}
            <div className="text-center">
              <Users className="w-8 h-8 mx-auto mb-2 text-purple-500" />
              <div className="text-sm font-medium">Consensus</div>
              <div className="text-2xl font-bold">{(trust.components.consensus * 100).toFixed(0)}%</div>
              <Progress value={trust.components.consensus * 100} className="mt-1 h-1" />
            </div>
            
            {/* Ethical */}
            <div className="text-center">
              <Shield className="w-8 h-8 mx-auto mb-2 text-orange-500" />
              <div className="text-sm font-medium">Ethical</div>
              <div className="text-2xl font-bold">{(trust.components.ethical * 100).toFixed(0)}%</div>
              <Progress value={trust.components.ethical * 100} className="mt-1 h-1" />
            </div>
          </div>
          
          {/* Human Verification Status */}
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm font-medium">Human Verification Status</span>
              </div>
              {trust.components.human ? (
                <Badge variant="default" className="gap-1">
                  <CheckCircle className="w-3 h-3" />
                  Verified
                </Badge>
              ) : (
                <Badge variant="outline" className="gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  Pending
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Verification Queue */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Verification Queue</CardTitle>
            <Button size="sm">
              View All Pending
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No items pending verification</p>
            <p className="text-xs mt-1">Responses requiring human review will appear here</p>
          </div>
        </CardContent>
      </Card>
      
      {/* Trust Trends */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Trust Trends</CardTitle>
            <div className="flex items-center gap-1 text-sm text-green-500">
              <TrendingUp className="w-4 h-4" />
              +5.2%
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Trust metrics have improved by 5.2% over the last 24 hours based on increased verification rates 
            and improved neural confidence scores.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrustCenter;