import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Shield,
  CheckCircle,
  XCircle,
  AlertCircle,
  Brain,
  Sparkles,
  Activity,
  TrendingUp,
  Database,
  Zap
} from 'lucide-react';
import { hallucinationAPI, ValidationResult, Statistics, QualityAnalysisResult } from '@/services/hallucinationPreventionService';
import { toast } from 'sonner';

// Import new tab components
import { BatchProcessingTab } from './BatchProcessingTab';
import { GovernanceTab } from './GovernanceTab';

export const HallucinationPrevention: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [factInput, setFactInput] = useState('');
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [qualityAnalysis, setQualityAnalysis] = useState<QualityAnalysisResult | null>(null);
  const [healthStatus, setHealthStatus] = useState<'online' | 'offline' | 'checking'>('checking');

  // Load initial data
  useEffect(() => {
    checkSystemHealth();
    loadStatistics();
  }, []);

  const checkSystemHealth = async () => {
    try {
      const isHealthy = await hallucinationAPI.checkHealth();
      setHealthStatus(isHealthy ? 'online' : 'offline');
    } catch (error) {
      setHealthStatus('offline');
      toast.error('Could not connect to Hallucination Prevention API');
    }
  };

  const loadStatistics = async () => {
    try {
      const stats = await hallucinationAPI.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const handleValidateFact = async () => {
    if (!factInput.trim()) {
      toast.error('Please enter a fact to validate');
      return;
    }

    setLoading(true);
    try {
      const result = await hallucinationAPI.validateFact(factInput);
      setValidationResult(result);
      
      // Refresh statistics after validation
      await loadStatistics();
      
      if (result.valid) {
        toast.success(`Fact is VALID with ${((result.confidence || 0) * 100).toFixed(1)}% confidence`);
      } else {
        toast.error(`Fact is INVALID with ${((result.confidence || 0) * 100).toFixed(1)}% confidence`);
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleQualityAnalysis = async () => {
    setLoading(true);
    try {
      const analysis = await hallucinationAPI.runQualityAnalysis();
      setQualityAnalysis(analysis);
      
      toast.success(`Quality Analysis Complete: Analyzed ${analysis.analysis.total_facts} facts`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'text-green-500';
    if (confidence >= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getStatusBadge = () => {
    switch (healthStatus) {
      case 'online':
        return <Badge className="bg-green-500">Online</Badge>;
      case 'offline':
        return <Badge variant="destructive">Offline</Badge>;
      default:
        return <Badge variant="secondary">Checking...</Badge>;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="h-8 w-8 text-purple-500" />
          <div>
            <h1 className="text-3xl font-bold">Hallucination Prevention</h1>
            <p className="text-muted-foreground">AI-Powered Fact Validation & Quality Assurance</p>
          </div>
        </div>
        {getStatusBadge()}
      </div>

      {/* Statistics Overview */}
      {statistics && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Validated</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_validated || 0}</div>
              <p className="text-xs text-muted-foreground">
                {statistics.cache_hits || 0} from cache
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Invalid Found</CardTitle>
              <XCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.invalid_found || 0}</div>
              <p className="text-xs text-muted-foreground">
                {statistics.corrections_suggested || 0} corrections
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Time</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(statistics.validation_time_avg || 0).toFixed(2)}s</div>
              <p className="text-xs text-muted-foreground">per validation</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Threshold</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{((statistics.validation_threshold || 0.8) * 100).toFixed(0)}%</div>
              <p className="text-xs text-muted-foreground">
                {statistics.auto_validation_enabled ? 'Auto-enabled' : 'Manual'}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="validate" className="space-y-4">
        <TabsList>
          <TabsTrigger value="validate">Validate Facts</TabsTrigger>
          <TabsTrigger value="quality">Quality Analysis</TabsTrigger>
          <TabsTrigger value="batch">Batch Processing</TabsTrigger>
          <TabsTrigger value="governance">Governance</TabsTrigger>
        </TabsList>

        {/* Single Fact Validation Tab */}
        <TabsContent value="validate" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Fact Validation</CardTitle>
              <CardDescription>
                Enter a fact to validate using multiple AI-powered validators
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Fact Statement</label>
                <Textarea
                  placeholder="e.g., HasProperty(water, liquid)"
                  value={factInput}
                  onChange={(e) => setFactInput(e.target.value)}
                  className="min-h-[100px]"
                />
              </div>
              
              <Button 
                onClick={handleValidateFact}
                disabled={loading || !factInput.trim()}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Activity className="mr-2 h-4 w-4 animate-spin" />
                    Validating...
                  </>
                ) : (
                  <>
                    <Shield className="mr-2 h-4 w-4" />
                    Validate Fact
                  </>
                )}
              </Button>

              {/* Validation Result */}
              {validationResult && (
                <Alert className={validationResult.valid ? 'border-green-500' : 'border-red-500'}>
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle className="flex items-center justify-between">
                    <span>Validation Result: {validationResult.valid ? 'VALID' : 'INVALID'}</span>
                    <Badge className={getConfidenceColor(validationResult.confidence)}>
                      {((validationResult.confidence || 0) * 100).toFixed(1)}% Confidence
                    </Badge>
                  </AlertTitle>
                  <AlertDescription className="mt-2 space-y-2">
                    <div>
                      <strong>Category:</strong> {validationResult.category}
                    </div>
                    <div>
                      <strong>Reasoning:</strong> {validationResult.reasoning}
                    </div>
                    {validationResult.issues && validationResult.issues.length > 0 && (
                      <div>
                        <strong>Issues:</strong>
                        <ul className="list-disc list-inside mt-1">
                          {validationResult.issues.map((issue, idx) => (
                            <li key={idx}>{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {validationResult.correction && (
                      <div>
                        <strong>Suggested Correction:</strong> {validationResult.correction}
                      </div>
                    )}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Available Validators */}
          {statistics && statistics.validators_available && (
            <Card>
              <CardHeader>
                <CardTitle>Available Validators</CardTitle>
                <CardDescription>Active validation engines</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(statistics.validators_available).map(([name, enabled]) => (
                    <div key={name} className="flex items-center justify-between">
                      <span className="capitalize">{name.replace('_', ' ')}</span>
                      <Badge variant={enabled ? 'default' : 'secondary'}>
                        {enabled ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Quality Analysis Tab */}
        <TabsContent value="quality" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Knowledge Base Quality Analysis</CardTitle>
              <CardDescription>
                Analyze the quality of facts in the knowledge base
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                onClick={handleQualityAnalysis}
                disabled={loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Activity className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    Run Quality Analysis
                  </>
                )}
              </Button>

              {qualityAnalysis && qualityAnalysis.success && (
                <div className="space-y-4">
                  <Alert>
                    <Sparkles className="h-4 w-4" />
                    <AlertTitle>Analysis Complete</AlertTitle>
                    <AlertDescription>
                      <div className="mt-2 space-y-2">
                        <div>
                          <strong>Total Facts:</strong> {qualityAnalysis.analysis.total_facts}
                        </div>
                        <div>
                          <strong>HasProperty Percentage:</strong> {(qualityAnalysis.analysis.hasproperty_percent || 0).toFixed(1)}%
                        </div>
                        <div>
                          <strong>Assessment:</strong> {qualityAnalysis.analysis.quality_assessment}
                        </div>
                      </div>
                    </AlertDescription>
                  </Alert>

                  {/* Predicate Distribution */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Predicate Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {Object.entries(qualityAnalysis.analysis.predicates).map(([predicate, count]) => (
                          <div key={predicate} className="flex items-center justify-between">
                            <span>{predicate}</span>
                            <div className="flex items-center gap-2">
                              <Progress 
                                value={(count / qualityAnalysis.analysis.total_facts) * 100} 
                                className="w-32"
                              />
                              <span className="text-sm text-muted-foreground w-12 text-right">
                                {count}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Batch Processing Tab */}
        <TabsContent value="batch" className="space-y-4">
          <BatchProcessingTab onValidationComplete={loadStatistics} />
        </TabsContent>

        {/* Governance Tab */}
        <TabsContent value="governance" className="space-y-4">
          <GovernanceTab onComplianceCheck={loadStatistics} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default HallucinationPrevention;
