// TrustScoreCard.tsx - Kritische Komponente für Vertrauenswürdigkeit
// Nach HAK/GAL Artikel 3 (Externe Verifikation) & Artikel 6 (Empirische Validierung)

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  Shield, Brain, Database, Users, CheckCircle, 
  AlertTriangle, Info, ExternalLink, Zap
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface TrustComponents {
  neuralConfidence: number;      // HRM confidence (0-1)
  factualAccuracy: number;        // Fabulometer score (0-1)
  sourceQuality: number;          // KB citation quality (0-1)
  consensus: number;              // LLM agreement (0-1)
  humanVerified: boolean;         // Manual verification
  ethicalAlignment: number;       // Philosophical Intelligence (0-1)
}

export interface TrustScoreProps {
  query: string;
  response: string;
  components: TrustComponents;
  sources?: Array<{
    fact: string;
    confidence: number;
    id: string;
  }>;
  onVerify?: () => void;
  className?: string;
}

const TrustScoreCard: React.FC<TrustScoreProps> = ({
  query,
  response,
  components,
  sources = [],
  onVerify,
  className
}) => {
  // Calculate overall trust score (weighted average)
  const calculateOverallTrust = () => {
    const weights = {
      neuralConfidence: 0.25,
      factualAccuracy: 0.25,
      sourceQuality: 0.20,
      consensus: 0.20,
      ethicalAlignment: 0.10
    };
    
    let score = 
      components.neuralConfidence * weights.neuralConfidence +
      components.factualAccuracy * weights.factualAccuracy +
      components.sourceQuality * weights.sourceQuality +
      components.consensus * weights.consensus +
      components.ethicalAlignment * weights.ethicalAlignment;
    
    // Boost for human verification
    if (components.humanVerified) {
      score = Math.min(1, score * 1.1);
    }
    
    return score;
  };
  
  const overallTrust = calculateOverallTrust();
  
  // Determine trust level and styling
  const getTrustLevel = (score: number) => {
    if (score >= 0.8) return { label: 'HIGH', color: 'text-green-500', bg: 'bg-green-500/10' };
    if (score >= 0.6) return { label: 'MEDIUM', color: 'text-yellow-500', bg: 'bg-yellow-500/10' };
    if (score >= 0.4) return { label: 'LOW', color: 'text-orange-500', bg: 'bg-orange-500/10' };
    return { label: 'VERY LOW', color: 'text-red-500', bg: 'bg-red-500/10' };
  };
  
  const trustLevel = getTrustLevel(overallTrust);
  
  // Component metric display
  const MetricRow = ({ 
    icon: Icon, 
    label, 
    value, 
    max = 1,
    showBar = true,
    verified = false 
  }: any) => {
    const percentage = (value / max) * 100;
    const color = value >= 0.7 ? 'text-green-500' : value >= 0.4 ? 'text-yellow-500' : 'text-red-500';
    
    return (
      <div className="flex items-center justify-between py-2">
        <div className="flex items-center gap-2 flex-1">
          <Icon className={cn("w-4 h-4", color)} />
          <span className="text-sm font-medium">{label}</span>
          {verified && <CheckCircle className="w-3 h-3 text-green-500" />}
        </div>
        <div className="flex items-center gap-3 flex-1">
          {showBar && (
            <Progress value={percentage} className="flex-1 h-2" />
          )}
          <span className={cn("text-sm font-mono min-w-[3rem] text-right", color)}>
            {(value * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    );
  };
  
  return (
    <Card className={cn("relative overflow-hidden", className)}>
      {/* Animated trust level indicator */}
      <motion.div
        className={cn("absolute top-0 left-0 right-0 h-1", trustLevel.bg)}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: overallTrust }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      />
      
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Shield className={cn("w-5 h-5", trustLevel.color)} />
            Trust Analysis
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge 
              variant={overallTrust >= 0.7 ? "default" : "secondary"}
              className={cn("font-mono", trustLevel.bg, trustLevel.color)}
            >
              {(overallTrust * 100).toFixed(0)}% {trustLevel.label}
            </Badge>
            {components.humanVerified && (
              <Badge variant="outline" className="text-green-500 border-green-500">
                <CheckCircle className="w-3 h-3 mr-1" />
                Verified
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Query & Response Preview */}
        <div className="p-3 bg-muted/50 rounded-lg space-y-2">
          <div className="text-xs text-muted-foreground">Query</div>
          <div className="text-sm font-medium">{query}</div>
          <div className="text-xs text-muted-foreground mt-2">Response</div>
          <div className="text-sm line-clamp-2">{response}</div>
        </div>
        
        {/* Trust Components Breakdown */}
        <div className="space-y-1">
          <MetricRow
            icon={Brain}
            label="Neural Confidence"
            value={components.neuralConfidence}
            verified={components.neuralConfidence > 0.85}
          />
          <MetricRow
            icon={Database}
            label="Factual Accuracy"
            value={components.factualAccuracy}
          />
          <MetricRow
            icon={ExternalLink}
            label="Source Quality"
            value={components.sourceQuality}
          />
          <MetricRow
            icon={Users}
            label="Model Consensus"
            value={components.consensus}
          />
          <MetricRow
            icon={Zap}
            label="Ethical Alignment"
            value={components.ethicalAlignment}
          />
        </div>
        
        {/* Source Citations */}
        {sources.length > 0 && (
          <div className="pt-3 border-t">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Sources ({sources.length})</span>
              <Button variant="ghost" size="sm" className="h-6 text-xs">
                View All
                <ExternalLink className="w-3 h-3 ml-1" />
              </Button>
            </div>
            <div className="space-y-1">
              {sources.slice(0, 3).map((source, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <code className="font-mono truncate flex-1">{source.fact}</code>
                  <Badge variant="outline" className="ml-2 text-xs">
                    {(source.confidence * 100).toFixed(0)}%
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Warning for low trust */}
        {overallTrust < 0.5 && (
          <div className="flex items-start gap-2 p-3 bg-orange-500/10 rounded-lg">
            <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5" />
            <div className="flex-1">
              <div className="text-sm font-medium text-orange-500">Low Confidence Response</div>
              <div className="text-xs text-muted-foreground mt-1">
                This response has low trust indicators. Consider requesting additional verification or alternative sources.
              </div>
            </div>
          </div>
        )}
        
        {/* Human Verification */}
        {!components.humanVerified && onVerify && (
          <div className="flex items-center justify-between pt-3 border-t">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Info className="w-4 h-4" />
              <span>Help improve accuracy</span>
            </div>
            <Button
              variant="default"
              size="sm"
              onClick={onVerify}
            >
              <CheckCircle className="w-3 h-3 mr-1" />
              Verify Response
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TrustScoreCard;

// Companion component for inline trust indicators
export const TrustBadge: React.FC<{ score: number; compact?: boolean }> = ({ 
  score, 
  compact = false 
}) => {
  const level = score >= 0.8 ? 'high' : score >= 0.6 ? 'medium' : score >= 0.4 ? 'low' : 'very-low';
  const colors = {
    'high': 'bg-green-500/10 text-green-500 border-green-500/20',
    'medium': 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    'low': 'bg-orange-500/10 text-orange-500 border-orange-500/20',
    'very-low': 'bg-red-500/10 text-red-500 border-red-500/20'
  };
  
  if (compact) {
    return (
      <div className={cn(
        "inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium border",
        colors[level]
      )}>
        <Shield className="w-3 h-3" />
        {(score * 100).toFixed(0)}%
      </div>
    );
  }
  
  return (
    <Badge variant="outline" className={cn("gap-1", colors[level])}>
      <Shield className="w-3 h-3" />
      Trust: {(score * 100).toFixed(0)}%
    </Badge>
  );
};

// Radar chart for trust visualization (requires recharts)
export const TrustRadar: React.FC<{ components: TrustComponents }> = ({ components }) => {
  // Implementation would use recharts RadarChart
  // Placeholder for now
  return (
    <div className="flex items-center justify-center h-48 text-muted-foreground">
      <div className="text-center">
        <Shield className="w-8 h-8 mx-auto mb-2" />
        <div className="text-sm">Trust Radar Visualization</div>
        <div className="text-xs">Requires recharts integration</div>
      </div>
    </div>
  );
};