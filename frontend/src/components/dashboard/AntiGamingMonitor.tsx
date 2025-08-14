import React from 'react';
import { Shield, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const AntiGamingMonitor = () => {
  return (
    <Card className="h-full border-0 bg-card/50">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Anti-Gaming Monitor
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
          <AlertTriangle className="w-5 h-5 text-yellow-500" />
          <p className="text-sm text-muted-foreground">
            Feature not implemented. This component is a placeholder.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default AntiGamingMonitor;
