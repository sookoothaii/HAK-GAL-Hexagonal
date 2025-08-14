// src/components/dashboard/LiveRewardChart.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useGovernorStore } from '@/stores/useGovernorStore';

const LiveRewardChart = () => {
  const rewardHistory = useGovernorStore(state => state.rewardHistory);
  
  // Transform data for recharts
  const chartData = rewardHistory.map(point => ({
    time: new Date(point.timestamp).toLocaleTimeString(),
    reward: point.reward,
    action: point.action
  }));

  return (
    <div className="h-full w-full p-4 rounded-lg border border-border bg-card">
      <h3 className="text-lg font-semibold mb-4">Live Reward Tracking</h3>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="time" stroke="#888" />
          <YAxis stroke="#888" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
            labelStyle={{ color: '#888' }}
          />
          <Line 
            type="monotone" 
            dataKey="reward" 
            stroke="hsl(var(--primary))" 
            strokeWidth={2}
            dot={{ fill: 'hsl(var(--primary))' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LiveRewardChart;
