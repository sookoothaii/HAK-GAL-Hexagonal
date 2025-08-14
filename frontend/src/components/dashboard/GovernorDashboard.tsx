// src/components/dashboard/GovernorDashboard.tsx
import React from 'react';
import LiveRewardChart from './LiveRewardChart';
import KbMetricsDisplay from './KbMetricsDisplay';
import { Separator } from '@/components/ui/separator';

const GovernorDashboard = () => {
  return (
    <div className="h-full w-full flex flex-col gap-4">
      <div className="flex-1">
        <KbMetricsDisplay />
      </div>
      
      <Separator />

      <div className="flex-1">
        <LiveRewardChart />
      </div>
    </div>
  );
};

export default GovernorDashboard;
