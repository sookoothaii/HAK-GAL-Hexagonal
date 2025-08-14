import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const VeritasEngine = () => {
  return (
    <Card className="h-full border-0 bg-card/50">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-yellow-500" />
          Veritas Engine (Coming Soon)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          The Veritas Engine for formal verification is currently under development.
          This feature will be available in a future release.
        </p>
      </CardContent>
    </Card>
  );
};

export default VeritasEngine;
