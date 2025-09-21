import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import {
  Shield,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Activity,
  Lock,
  Zap,
  Brain,
  FileText,
  ShieldCheck
} from 'lucide-react';
import { hallucinationAPI } from '@/services/hallucinationPreventionService';
import { toast } from 'sonner';

interface GovernanceTabProps {
  onComplianceCheck?: () => void;
}

interface ComplianceResult {
  compliant: boolean;
  confidence: number;
  governance_checks_passed: {
    structural: boolean;
    scientific: boolean;
    content_safety: boolean;
  };
  issues: string[];
}

export const GovernanceTab: React.FC<GovernanceTabProps> = ({ onComplianceCheck }) => {
  const [loading, setLoading] = useState(false);
  const [factInput, setFactInput] = useState('');
  const [complianceResult, setComplianceResult] = useState<ComplianceResult | null>(null);
  const [history, setHistory] = useState<Array<{
    fact: string;
    compliant: boolean;
    timestamp: string;
  }>>([]);

  const handleComplianceCheck = async () => {
    if (!factInput.trim()) {
      toast.error('Please enter a fact to check for governance compliance');
      return;
    }

    setLoading(true);
    try {
      const result = await hallucinationAPI.checkGovernanceCompliance(factInput);
      setComplianceResult(result);
      
      // Add to history
      setHistory(prev => [{
        fact: factInput,
        compliant: result.compliant,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev.slice(0, 9)]); // Keep last 10

      if (result.compliant) {
        toast.success('✅ Fact meets all governance standards');
      } else {
        toast.error('❌ Fact violates governance standards');
      }

      if (onComplianceCheck) {
        onComplianceCheck();
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadExampleFact = (type: 'good' | 'bad') => {
    const examples = {
      good: 'HasProperty(water, liquid, H2O, transparent, essential_for_life, chemical_compound)',
      bad: 'HasProperty(water,liquid)' // Missing trailing dot, insufficient arguments
    };
    setFactInput(examples[type]);
  };

  const getCheckIcon = (passed: boolean) => {
    return passed ? (
      <CheckCircle className="h-4 w-4 text-green-500" />
    ) : (
      <XCircle className="h-4 w-4 text-red-500" />
    );
  };

  const getComplianceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-4">
      {/* Governance Standards Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            HAK-GAL Governance Standards
          </CardTitle>
          <CardDescription>
            Facts must comply with three core governance pillars
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-blue-500" />
                <h4 className="font-semibold">Structural Integrity</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Proper n-ary format, PascalCase predicates, correct syntax
              </p>
              <ul className="text-xs space-y-1 text-muted-foreground">
                <li>• Valid predicate format</li>
                <li>• Minimum 6 arguments</li>
                <li>• Trailing dot required</li>
              </ul>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4 text-purple-500" />
                <h4 className="font-semibold">Scientific Accuracy</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Empirically verifiable, logically consistent facts
              </p>
              <ul className="text-xs space-y-1 text-muted-foreground">
                <li>• No contradictions</li>
                <li>• Verifiable claims</li>
                <li>• Scientific rigor</li>
              </ul>
            </div>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Lock className="h-4 w-4 text-orange-500" />
                <h4 className="font-semibold">Content Safety</h4>
              </div>
              <p className="text-sm text-muted-foreground">
                Safe, ethical, and appropriate content standards
              </p>
              <ul className="text-xs space-y-1 text-muted-foreground">
                <li>• No harmful content</li>
                <li>• Ethical compliance</li>
                <li>• Privacy protection</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Compliance Checker */}
      <Card>
        <CardHeader>
          <CardTitle>Governance Compliance Checker</CardTitle>
          <CardDescription>
            Validate facts against HAK-GAL governance standards
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Fact to Check</label>
            <Textarea
              placeholder="e.g., HasProperty(entity, property1, property2, property3, property4, property5)"
              value={factInput}
              onChange={(e) => setFactInput(e.target.value)}
              className="min-h-[100px] font-mono"
            />
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadExampleFact('good')}
              >
                Load Good Example
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadExampleFact('bad')}
              >
                Load Bad Example
              </Button>
            </div>
          </div>

          <Button
            onClick={handleComplianceCheck}
            disabled={loading || !factInput.trim()}
            className="w-full"
          >
            {loading ? (
              <>
                <Activity className="mr-2 h-4 w-4 animate-spin" />
                Checking Compliance...
              </>
            ) : (
              <>
                <ShieldCheck className="mr-2 h-4 w-4" />
                Check Governance Compliance
              </>
            )}
          </Button>

          {/* Compliance Result */}
          {complianceResult && (
            <div className="space-y-4">
              <Alert className={complianceResult.compliant ? 'border-green-500' : 'border-red-500'}>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>
                  Governance Compliance: {complianceResult.compliant ? 'PASSED ✅' : 'FAILED ❌'}
                </AlertTitle>
                <AlertDescription className="mt-2">
                  <div className="space-y-3">
                    {/* Confidence Score */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span>Confidence Level</span>
                        <span>{((complianceResult.confidence || 0) * 100).toFixed(1)}%</span>
                      </div>
                      <Progress 
                        value={complianceResult.confidence * 100} 
                        className={`h-2 ${getComplianceColor(complianceResult.confidence)}`}
                      />
                    </div>

                    {/* Individual Checks */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-semibold">Compliance Checks:</h4>
                      <div className="grid grid-cols-3 gap-2">
                        <div className="flex items-center gap-1">
                          {getCheckIcon(complianceResult.governance_checks_passed.structural)}
                          <span className="text-xs">Structural</span>
                        </div>
                        <div className="flex items-center gap-1">
                          {getCheckIcon(complianceResult.governance_checks_passed.scientific)}
                          <span className="text-xs">Scientific</span>
                        </div>
                        <div className="flex items-center gap-1">
                          {getCheckIcon(complianceResult.governance_checks_passed.content_safety)}
                          <span className="text-xs">Safety</span>
                        </div>
                      </div>
                    </div>

                    {/* Issues */}
                    {complianceResult.issues.length > 0 && (
                      <div className="space-y-1">
                        <h4 className="text-sm font-semibold">Issues Found:</h4>
                        <ul className="text-xs space-y-1">
                          {complianceResult.issues.map((issue, idx) => (
                            <li key={idx} className="flex items-start gap-1">
                              <span className="text-red-500 mt-0.5">•</span>
                              <span>{issue}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </AlertDescription>
              </Alert>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Compliance History */}
      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Compliance Checks</CardTitle>
            <CardDescription>
              Last {history.length} compliance checks in this session
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {history.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-muted/50">
                  <div className="flex items-center gap-2">
                    {item.compliant ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="text-sm font-mono truncate max-w-[300px]">
                      {item.fact}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={item.compliant ? 'default' : 'destructive'} className="text-xs">
                      {item.compliant ? 'Compliant' : 'Non-compliant'}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {item.timestamp}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Governance Tips */}
      <Alert>
        <Zap className="h-4 w-4" />
        <AlertTitle>Pro Tips</AlertTitle>
        <AlertDescription>
          <ul className="text-sm space-y-1 mt-2">
            <li>• Facts must have at least 6 arguments for comprehensive validation</li>
            <li>• Always include a trailing dot at the end of facts</li>
            <li>• Use PascalCase for predicate names (e.g., HasProperty, IsA)</li>
            <li>• Arguments should be separated by commas without spaces</li>
          </ul>
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default GovernanceTab;
