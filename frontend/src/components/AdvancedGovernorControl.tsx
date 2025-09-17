// Advanced Governor Control Component
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Rocket, Zap, AlertCircle } from 'lucide-react';

interface AdvancedGovernorControlProps {
  onRefresh?: () => void;
}

const AdvancedGovernorControl: React.FC<AdvancedGovernorControlProps> = ({ onRefresh }) => {
  const [status, setStatus] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const forceOptimizedGenerator = async () => {
    setLoading(true);
    setStatus('Activating optimized generator...');
    
    try {
      // Step 1: Stop current governor
      setStatus('Stopping current governor...');
      await fetch('http://localhost:5002/api/governor/stop', {
        method: 'POST'
      });
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Step 2: Start with special flag for optimized generator
      setStatus('Starting optimized generator...');
      const response = await fetch('http://localhost:5002/api/governor/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          use_llm: true,
          mode: 'optimized_generator',
          features: {
            duplicate_prevention: true,
            balanced_predicates: true,
            has_property_limit: 0.2
          }
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setStatus('✅ Optimized generator activated!');
        
        // Check if it's really the optimized version
        if (result.optimized) {
          setStatus('✅✅ OPTIMIZED Generator confirmed! HasProperty limited to 20%');
        } else {
          setStatus('⚠️ Generator started but not optimized version');
        }
        
        if (onRefresh) {
          setTimeout(onRefresh, 2000);
        }
      } else {
        setStatus('❌ Failed to start generator');
      }
      
    } catch (error) {
      console.error('Error:', error);
      setStatus('❌ Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const checkGeneratorStatus = async () => {
    try {
      const response = await fetch('http://localhost:5002/api/llm-governor/status');
      const data = await response.json();
      
      let statusMsg = '';
      if (data.generating) {
        statusMsg += `✅ Generator RUNNING\n`;
        statusMsg += `Optimized: ${data.optimized ? '✅ YES' : '❌ NO'}\n`;
        
        if (data.metrics) {
          statusMsg += `Facts generated: ${data.metrics.facts_generated}\n`;
          statusMsg += `Rate: ${data.metrics.facts_per_minute?.toFixed(1)} facts/min\n`;
          statusMsg += `HasProperty %: ${data.metrics.has_property_percentage?.toFixed(1)}%\n`;
          statusMsg += `Predicate diversity: ${data.metrics.predicate_diversity} types`;
        }
      } else {
        statusMsg = '❌ Generator NOT running';
      }
      
      setStatus(statusMsg);
    } catch (error) {
      setStatus('❌ Cannot check status: ' + error.message);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Rocket className="w-5 h-5 text-purple-500" />
          Advanced Generator Control
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Optimized Generator Features:</strong>
            <br />• HasProperty limited to 20% (was 78%)
            <br />• Duplicate prevention via argument normalization
            <br />• 15 balanced predicate types
            <br />• Extended entity pools for diversity
          </AlertDescription>
        </Alert>

        <div className="flex gap-2">
          <Button
            onClick={forceOptimizedGenerator}
            disabled={loading}
            className="flex-1"
            variant="default"
          >
            <Zap className="w-4 h-4 mr-2" />
            {loading ? 'Activating...' : 'Force Optimized Generator'}
          </Button>
          
          <Button
            onClick={checkGeneratorStatus}
            variant="outline"
          >
            Check Status
          </Button>
        </div>

        {status && (
          <div className="p-3 bg-muted rounded-lg font-mono text-xs whitespace-pre-line">
            {status}
          </div>
        )}

        <div className="text-xs text-muted-foreground">
          <p>If the generator doesn't start with optimized features:</p>
          <ol className="list-decimal list-inside mt-1">
            <li>Close the backend terminal window</li>
            <li>Delete all __pycache__ folders</li>
            <li>Restart: <code>python hexagonal_api_enhanced_clean.py</code></li>
            <li>Click "Force Optimized Generator" again</li>
          </ol>
        </div>
      </CardContent>
    </Card>
  );
};

export default AdvancedGovernorControl;