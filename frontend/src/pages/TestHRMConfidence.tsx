// TestHRMConfidence.tsx - Test page for HRM confidence display
import React, { useState } from 'react';
import { TrustAnalysisWrapper } from '@/components/TrustAnalysisWrapper';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const TestHRMConfidence = () => {
  const [testQuery, setTestQuery] = useState('IsA(Socrates, Philosopher).');
  const [testResponse, setTestResponse] = useState('Socrates is indeed a philosopher.');
  
  const testQueries = [
    { query: 'IsA(Socrates, Philosopher).', expected: 1.0 },
    { query: 'HasPart(Computer, CPU).', expected: 1.0 },
    { query: 'IsA(Water, Person).', expected: 0.01 },
  ];
  
  const runTest = (query: string) => {
    setTestQuery(query);
    setTestResponse(`Testing: ${query}`);
  };
  
  return (
    <div className="p-4 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>HRM Confidence Test Page</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            {testQueries.map((test, idx) => (
              <Button
                key={idx}
                onClick={() => runTest(test.query)}
                variant="outline"
                size="sm"
              >
                Test {idx + 1} (Expected: {(test.expected * 100).toFixed(0)}%)
              </Button>
            ))}
          </div>
          
          <div className="text-sm text-muted-foreground">
            Current Query: <code>{testQuery}</code>
          </div>
          
          <TrustAnalysisWrapper
            query={testQuery}
            response={testResponse}
            sources={[]}
          />
          
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium mb-2">Debug Console:</p>
            <p className="text-xs font-mono">
              Open browser console and run: window.testHRM('IsA(Socrates, Philosopher).')
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TestHRMConfidence;
