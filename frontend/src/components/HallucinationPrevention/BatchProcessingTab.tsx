import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import {
  Database,
  CheckCircle,
  XCircle,
  AlertCircle,
  Activity,
  FileText,
  Download,
  Upload
} from 'lucide-react';
import { hallucinationAPI, BatchValidationResult } from '@/services/hallucinationPreventionService';
import { toast } from 'sonner';

interface BatchProcessingTabProps {
  onValidationComplete?: () => void;
}

export const BatchProcessingTab: React.FC<BatchProcessingTabProps> = ({ onValidationComplete }) => {
  const [loading, setLoading] = useState(false);
  const [factIdsInput, setFactIdsInput] = useState('');
  const [validationLevel, setValidationLevel] = useState<'basic' | 'comprehensive' | 'strict'>('comprehensive');
  const [batchResult, setBatchResult] = useState<BatchValidationResult | null>(null);

  const handleBatchValidation = async () => {
    // Parse fact IDs from input
    const factIds = factIdsInput
      .split(/[,\s]+/)
      .map(id => parseInt(id.trim()))
      .filter(id => !isNaN(id));

    if (factIds.length === 0) {
      toast.error('Please enter valid fact IDs (comma or space separated)');
      return;
    }

    setLoading(true);
    try {
      const result = await hallucinationAPI.validateBatch(factIds, validationLevel);
      setBatchResult(result);
      
      if (result.success_rate > 0.8) {
        toast.success(`Batch Validation Complete: Validated ${result.total_facts} facts in ${(result.duration || 0).toFixed(2)}s`);
      } else {
        toast.warning(`Batch Validation Complete: Validated ${result.total_facts} facts in ${(result.duration || 0).toFixed(2)}s - Success rate: ${((result.success_rate || 0) * 100).toFixed(1)}%`);
      }

      if (onValidationComplete) {
        onValidationComplete();
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const exportResults = () => {
    if (!batchResult) return;

    const csvContent = [
      ['Fact ID', 'Fact', 'Valid', 'Confidence', 'Category', 'Issues', 'Correction'].join(','),
      ...batchResult.results.map(r => [
        r.fact_id || '',
        `"${r.fact || ''}"`,
        r.valid,
        r.confidence,
        r.category,
        `"${r.issues.join('; ')}"`,
        `"${r.correction || ''}"`,
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `batch_validation_${batchResult.batch_id}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const loadSampleFactIds = () => {
    // Load some sample fact IDs for testing
    setFactIdsInput('288, 314, 101, 102, 103, 104, 105');
    toast.info('Sample fact IDs loaded for testing');
  };

  return (
    <div className="space-y-4">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Batch Validation Setup</CardTitle>
          <CardDescription>
            Validate multiple facts at once by entering their IDs
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Fact IDs</label>
            <div className="flex gap-2">
              <Input
                placeholder="Enter fact IDs (e.g., 288, 314, 101)"
                value={factIdsInput}
                onChange={(e) => setFactIdsInput(e.target.value)}
                className="flex-1"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={loadSampleFactIds}
              >
                <Upload className="mr-2 h-4 w-4" />
                Load Sample
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Enter comma or space separated fact IDs from the knowledge base
            </p>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Validation Level</label>
            <Select value={validationLevel} onValueChange={(v) => setValidationLevel(v as any)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="basic">Basic - Quick structural check</SelectItem>
                <SelectItem value="comprehensive">Comprehensive - Full validation</SelectItem>
                <SelectItem value="strict">Strict - Maximum scrutiny</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            onClick={handleBatchValidation}
            disabled={loading || !factIdsInput.trim()}
            className="w-full"
          >
            {loading ? (
              <>
                <Activity className="mr-2 h-4 w-4 animate-spin" />
                Processing Batch...
              </>
            ) : (
              <>
                <Database className="mr-2 h-4 w-4" />
                Validate Batch
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results Section */}
      {batchResult && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Batch Results</CardTitle>
                <CardDescription>
                  Batch ID: {batchResult.batch_id}
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={exportResults}
              >
                <Download className="mr-2 h-4 w-4" />
                Export CSV
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Total Facts</p>
                <p className="text-2xl font-bold">{batchResult.total_facts}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Valid Facts</p>
                <p className="text-2xl font-bold text-green-500">{batchResult.valid_facts}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Invalid Facts</p>
                <p className="text-2xl font-bold text-red-500">{batchResult.invalid_facts}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold">{((batchResult.success_rate || 0) * 100).toFixed(1)}%</p>
              </div>
            </div>

            <Separator />

            {/* Individual Results */}
            <div className="space-y-3">
              <h4 className="font-semibold">Individual Results</h4>
              <div className="max-h-[400px] overflow-y-auto space-y-2">
                {batchResult.results.map((result, idx) => (
                  <Alert key={idx} className={result.valid ? 'border-green-200' : 'border-red-200'}>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-2">
                        {result.valid ? (
                          <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500 mt-0.5" />
                        )}
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-sm">ID: {result.fact_id || 'N/A'}</span>
                            <Badge variant={result.valid ? 'default' : 'destructive'} className="text-xs">
                              {result.category}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {((result.confidence || 0) * 100).toFixed(1)}%
                            </Badge>
                          </div>
                          <p className="text-sm">{result.fact || 'No fact text'}</p>
                          {result.issues && result.issues.length > 0 && (
                            <div className="text-xs text-muted-foreground">
                              Issues: {result.issues.join(', ')}
                            </div>
                          )}
                          {result.correction && (
                            <div className="text-xs text-blue-600">
                              Suggestion: {result.correction}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </Alert>
                ))}
              </div>
            </div>

            {/* Processing Time */}
            <div className="text-sm text-muted-foreground text-right">
              Processed in {(batchResult.duration || 0).toFixed(3)} seconds
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default BatchProcessingTab;
