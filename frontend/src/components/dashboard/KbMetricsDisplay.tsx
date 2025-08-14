// src/components/dashboard/KbMetricsDisplay.tsx
import React from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';

const KbMetricsDisplay = () => {
  const kbMetrics = useGovernorStore(state => state.kbMetrics);
  
  const metrics = [
    { label: 'Fact Count', value: kbMetrics.factCount, unit: '' },
    { label: 'Growth Rate', value: kbMetrics.growthRate.toFixed(2), unit: '/min' },
    { label: 'Connectivity', value: kbMetrics.connectivity.toFixed(3), unit: '' },
    { label: 'Entropy', value: kbMetrics.entropy.toFixed(4), unit: '' }
  ];

  return (
    <div className="h-full w-full p-4 rounded-lg border border-border bg-card">
      <h3 className="text-lg font-semibold mb-4">Knowledge Base Metrics</h3>
      <div className="grid grid-cols-2 gap-3">
        {metrics.map((metric, idx) => (
          <div key={idx} className="p-3 rounded-md bg-background border border-border">
            <div className="text-sm text-muted-foreground">{metric.label}</div>
            <div className="text-xl font-semibold text-primary">
              {metric.value}
              <span className="text-sm text-muted-foreground ml-1">{metric.unit}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default KbMetricsDisplay;
