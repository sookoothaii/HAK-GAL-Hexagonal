import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Cpu, Thermometer, Zap, HardDrive, Fan, Activity } from 'lucide-react';
import { useGovernorStore } from '@/stores/useGovernorStore';

const CommandCenterGPUWidget: React.FC = () => {
  const gpuInfo = useGovernorStore(state => state.gpuInfo);
  
  // Use real data or default values
  const gpuData = gpuInfo || {
    name: 'No GPU Detected',
    utilization: 0,
    temperature: 0,
    memory_used: 0,
    memory_total: 1,
    memory_percent: 0,
    power_draw: null,
    power_limit: null,
    clock_speed: null,
    fan_speed: null
  };

  const formatMemory = (mb: number) => {
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(1)} GB`;
    }
    return `${mb} MB`;
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-medium">
          GPU Monitoring
        </CardTitle>
        <Badge variant="outline" className="text-xs">
          {gpuData.name || 'Unknown GPU'}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* GPU Utilization */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              GPU Usage
            </span>
            <span className="font-medium">{gpuData.utilization?.toFixed(0) || 0}%</span>
          </div>
          <Progress value={gpuData.utilization || 0} className="h-2" />
        </div>

        {/* Temperature */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <Thermometer className="w-4 h-4" />
              Temperature
            </span>
            <span className="font-medium">{gpuData.temperature?.toFixed(0) || 0}°C</span>
          </div>
          <Progress 
            value={Math.min((gpuData.temperature || 0) / 85 * 100, 100)} 
            className="h-2"
          />
        </div>

        {/* Memory Usage */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <HardDrive className="w-4 h-4" />
              Memory
            </span>
            <span className="font-medium">
              {formatMemory(gpuData.memory_used || 0)} / {formatMemory(gpuData.memory_total || 1)}
            </span>
          </div>
          <Progress value={gpuData.memory_percent || 0} className="h-2" />
        </div>

        {/* Power Draw (if available) */}
        {gpuData.power_draw !== null && gpuData.power_draw !== undefined && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Power Draw
              </span>
              <span className="font-medium">
                {gpuData.power_draw.toFixed(0)}W
                {gpuData.power_limit && ` / ${gpuData.power_limit.toFixed(0)}W`}
              </span>
            </div>
            {gpuData.power_limit && (
              <Progress 
                value={(gpuData.power_draw / gpuData.power_limit) * 100} 
                className="h-2" 
              />
            )}
          </div>
        )}

        {/* Clock Speed (if available) */}
        {gpuData.clock_speed !== null && gpuData.clock_speed !== undefined && (
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <Cpu className="w-4 h-4" />
              Clock Speed
            </span>
            <span className="font-medium">{gpuData.clock_speed} MHz</span>
          </div>
        )}

        {/* Fan Speed (if available) */}
        {gpuData.fan_speed !== null && gpuData.fan_speed !== undefined && (
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <Fan className="w-4 h-4" />
              Fan Speed
            </span>
            <span className="font-medium">{gpuData.fan_speed}%</span>
          </div>
        )}

        {/* Multi-GPU Summary (if available) */}
        {gpuInfo?.summary && gpuInfo.summary.gpu_count > 1 && (
          <div className="mt-4 pt-4 border-t space-y-2">
            <div className="text-sm font-medium">System Summary</div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>Total GPUs: {gpuInfo.summary.gpu_count}</div>
              <div>Avg Temp: {gpuInfo.summary.average_temperature?.toFixed(0)}°C</div>
              <div>Total Power: {gpuInfo.summary.total_power_draw?.toFixed(0)}W</div>
              <div>Avg Usage: {gpuInfo.summary.total_utilization?.toFixed(0)}%</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default CommandCenterGPUWidget;
