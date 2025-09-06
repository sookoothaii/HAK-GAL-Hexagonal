import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import {
  Shield, Brain, Database, Users, CheckCircle,
  AlertTriangle, Info, ExternalLink, Zap, Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

// --- Data Structures ---
interface SubMetric {
  label: string;
  value: string; // Can be 'N/A' or a percentage string like '90.0%'
  description: string;
}

interface TrustData {
  trust_score: {
    value: number;
    label: string;
  };
  sub_metrics: SubMetric[];
}

// --- Component Props ---
export interface TrustComponents {
  neuralConfidence: number;
  factualAccuracy: number;
  sourceQuality: number;
  consensus: number;
  humanVerified: boolean;
  ethicalAlignment: number;
}

export interface TrustScoreProps {
  query: string;
  response: string;
  // The 'components' prop is optional - if provided, skip API call
  components?: TrustComponents;
  onVerify?: () => void;
  className?: string;
}

const TrustScoreCard: React.FC<TrustScoreProps> = ({
  query,
  response,
  components,
  onVerify,
  className
}) => {
  // --- State Management for Fetched Data ---
  const [trustData, setTrustData] = useState<TrustData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // --- Data Fetching with useEffect ---
  useEffect(() => {
    // 🔧 FIX: If components are provided as props, use them directly
    if (components) {
      const trustData: TrustData = {
        trust_score: {
          value: calculateOverallTrust(components),
          label: 'Overall Trust Score'
        },
        sub_metrics: [
          {
            label: 'Factual Accuracy',
            value: `${(components.factualAccuracy * 100).toFixed(1)}%`,
            description: 'Based on facts found in knowledge base'
          },
          {
            label: 'Source Quality',
            value: `${(components.sourceQuality * 100).toFixed(1)}%`,
            description: 'Quality of sources used'
          },
          {
            label: 'Model Consensus',
            value: `${(components.consensus * 100).toFixed(1)}%`,
            description: 'Model confidence in response'
          },
          {
            label: 'Ethical Alignment',
            value: `${(components.ethicalAlignment * 100).toFixed(1)}%`,
            description: 'Alignment with ethical guidelines'
          },
          {
            label: 'Neural Confidence',
            value: `${(components.neuralConfidence * 100).toFixed(1)}%`,
            description: 'HRM neural reasoning confidence'
          }
        ]
      };
      setTrustData(trustData);
      setIsLoading(false);
      return;
    }
    
    // Otherwise fetch from backend (fallback)
    if (!query) {
      setTrustData(null);
      return;
    }

    const fetchTrustMetrics = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Fetch data from the new backend endpoint
        const response = await fetch(`http://127.0.0.1:5002/api/metrics/trust?query=${encodeURIComponent(query)}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: TrustData = await response.json();
        setTrustData(data);
      } catch (e) {
        console.error("Failed to fetch trust metrics:", e);
        setError("Could not load trust metrics.");
        setTrustData(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrustMetrics();
  }, [query, components]); // Re-run when query or components change
  
  // Helper function to calculate overall trust
  const calculateOverallTrust = (comp: TrustComponents): number => {
    // If humanVerified, return 100% - absolute trust
    if (comp.humanVerified) {
      return 100;
    }
    
    // Otherwise calculate normally
    const baseScore = (
      (comp.factualAccuracy || 0) * 0.3 +
      (comp.sourceQuality || 0) * 0.2 +
      (comp.consensus || 0) * 0.3 +
      (comp.ethicalAlignment || 0) * 0.2
    ) * 100;
    
    return baseScore;
  };

  // --- Helper Functions ---
  const getTrustLevel = (score: number) => {
    if (score >= 80) return { label: 'HIGH', color: 'text-green-500', bg: 'bg-green-500/10' };
    if (score >= 60) return { label: 'MEDIUM', color: 'text-yellow-500', bg: 'bg-yellow-500/10' };
    if (score >= 40) return { label: 'LOW', color: 'text-orange-500', bg: 'bg-orange-500/10' };
    return { label: 'VERY LOW', color: 'text-red-500', bg: 'bg-red-500/10' };
  };

  // --- Sub-Components ---
  const MetricRow = ({ icon: Icon, label, valueString }: { icon: React.ElementType, label: string, valueString: string }) => {
    const isNA = valueString === 'N/A';
    const percentage = isNA ? 0 : parseFloat(valueString.replace('%', ''));
    const color = percentage >= 70 ? 'text-green-500' : percentage >= 40 ? 'text-yellow-500' : 'text-red-500';

    return (
      <div className="flex items-center justify-between py-2">
        <div className="flex items-center gap-2 flex-1">
          <Icon className={cn("w-4 h-4", isNA ? 'text-muted-foreground' : color)} />
          <span className="text-sm font-medium">{label}</span>
        </div>
        <div className="flex items-center gap-3 flex-1">
          {!isNA && <Progress value={percentage} className="flex-1 h-2" />}
          <span className={cn("text-sm font-mono min-w-[4rem] text-right", isNA ? 'text-muted-foreground' : color)}>
            {valueString}
          </span>
        </div>
      </div>
    );
  };

  // --- Render Logic ---
  if (isLoading) {
    return (
      <Card className={cn("flex items-center justify-center p-10", className)}>
        <div className="text-center text-muted-foreground">
          <Loader2 className="w-8 h-8 mx-auto animate-spin mb-2" />
          <p>Analyzing Trust...</p>
        </div>
      </Card>
    );
  }

  if (error || !trustData) {
    return (
      <Card className={cn("flex items-center justify-center p-10", className)}>
        <div className="text-center text-red-500">
          <AlertTriangle className="w-8 h-8 mx-auto mb-2" />
          <p>{error || "Could not retrieve Trust Analysis."}</p>
        </div>
      </Card>
    );
  }

  const { trust_score, sub_metrics } = trustData;
  const trustLevel = getTrustLevel(trust_score.value);
      const isVerified = components?.humanVerified || false;
  const iconMap = { // Map labels to icons
    "Factual Accuracy": Database,
    "Neural Confidence": Brain,
    "Source Quality": ExternalLink,
    "Model Consensus": Users,
    "Ethical Alignment": Zap
  };

  return (
    <Card className={cn("relative overflow-hidden", className)}>
      <motion.div
        className={cn("absolute top-0 left-0 right-0 h-1", trustLevel.bg)}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: trust_score.value / 100 }}
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
              variant={trust_score.value >= 70 ? "default" : "secondary"}
              className={cn("font-mono", trustLevel.bg, trustLevel.color)}
            >
              {trust_score.value.toFixed(0)}% {trustLevel.label}
            </Badge>
            {isVerified && (
              <Badge variant="outline" className="text-xs bg-green-500/10 text-green-500 border-green-500/20">
                <CheckCircle className="w-3 h-3 mr-1" />
                Verified
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="p-3 bg-muted/50 rounded-lg space-y-2">
          <div className="text-xs text-muted-foreground">Query</div>
          <div className="text-sm font-medium">{query}</div>
        </div>
        
        <div className="space-y-1">
          {sub_metrics.map(metric => (
            <MetricRow
              key={metric.label}
              icon={iconMap[metric.label] || Shield}
              label={metric.label}
              valueString={metric.value}
            />
          ))}
        </div>
        
        {trust_score.value < 50 && (
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
        
        {onVerify && !isVerified && (
          <div className="flex items-center justify-between pt-3 border-t">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Info className="w-4 h-4" />
              <span>Help improve accuracy</span>
            </div>
            <Button variant="default" size="sm" onClick={onVerify}>
              <CheckCircle className="w-3 h-3 mr-1" />
              Verify Response
            </Button>
          </div>
        )}
        
        {onVerify && isVerified && (
          <div className="flex items-center justify-between pt-3 border-t">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-green-600">Response verified and locked</span>
            </div>
            <Badge variant="outline" className="text-xs bg-green-500/10 text-green-500 border-green-500/20">
              <CheckCircle className="w-3 h-3 mr-1" />
              Already Verified
            </Badge>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TrustScoreCard;

// Export types for use in other components
export type { TrustScoreProps, TrustComponents };

// Export TrustBadge placeholder
export const TrustBadge = Badge;
