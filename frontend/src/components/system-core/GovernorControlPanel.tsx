import React from 'react';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { wsService } from '@/hooks/useGovernorSocket';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Power, Activity, Brain, TrendingUp, Target, Zap } from 'lucide-react';

const GovernorControlPanel = () => {
  const {
    governor,
    kb,
    autoLearningConfig
  } = useGovernorStore();

  const governorStatus = governor.status;
  const governorRunning = governor.running;
  const governorDecisions = governor.decisions;
  const kbMetrics = kb.metrics;
  const qTableSize = governor.metrics?.qTableSize || 0;

  const handleToggleGovernor = () => {
    wsService.toggleGovernor(!governorRunning);
  };

  const handleToggleAutoLearning = (checked: boolean) => {
    wsService.toggleAutoLearning(checked);
    // Enhanced: Send detailed configuration to backend
    if (checked) {
      wsService.sendMessage('auto_learning_config', {
        enabled: true,
        loopIntervalSeconds: autoLearningConfig.loopIntervalSeconds,
        bootstrapThreshold: autoLearningConfig.bootstrapThreshold,
        explorationRate: autoLearningConfig.explorationRate,
        minCategoryCoverage: autoLearningConfig.minCategoryCoverage,
        minPfabScore: autoLearningConfig.minPfabScore,
        minKnowledgeGrowthRate: autoLearningConfig.minKnowledgeGrowthRate,
        minLlmHealth: autoLearningConfig.minLlmHealth
      });
    }
  };

  // Enhanced: Handle auto-learning status updates from backend
  const handleAutoLearningUpdate = (config: any) => {
    // Update store with backend configuration
    useGovernorStore.getState().updateAutoLearningConfig(config);
  };

  // Enhanced: Get real-time auto-learning status from backend
  const getAutoLearningStatus = () => {
    const config = autoLearningConfig;
    if (!config.enabled) return 'Disabled';
    if (!governorRunning) return 'Waiting for Governor';
    return 'Active - Learning';
  };

  // Enhanced: Calculate real metrics from backend data
  const getLearningMetrics = () => {
    const config = autoLearningConfig;
    return {
      explorationRate: (config.explorationRate * 100).toFixed(0),
      minPfabScore: config.minPfabScore,
      minCoverage: config.minCategoryCoverage,
      loopInterval: config.loopIntervalSeconds,
      bootstrapThreshold: config.bootstrapThreshold,
      minGrowthRate: config.minKnowledgeGrowthRate,
      minLlmHealth: config.minLlmHealth
    };
  };

  // Enhanced: Get comprehensive governor metrics
  const getGovernorMetrics = () => {
    const decisions = governorDecisions || [];
    const recentDecisions = decisions.slice(0, 10);
    const successfulDecisions = recentDecisions.filter((d: any) => d.executed).length;
    const successRate = recentDecisions.length > 0 
      ? (successfulDecisions / recentDecisions.length * 100).toFixed(1) 
      : '0';
    
    const avgReward = decisions.length > 0 
      ? decisions.reduce((sum: number, d: any) => sum + (d.reward || 0), 0) / decisions.length 
      : 0;
    
    const decisionTypes = decisions.reduce((acc: Record<string, number>, d: any) => {
      acc[d.type] = (acc[d.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return {
      successRate: parseFloat(successRate),
      avgReward: avgReward.toFixed(3),
      totalDecisions: decisions.length,
      decisionTypes,
      recentActivity: decisions.slice(0, 5)
    };
  };

  // Enhanced: Get governor strategy information
  const getGovernorStrategy = () => {
    const status = governorStatus as any;
    return {
      mode: status?.mode || 'CONSERVATIVE',
      algorithm: status?.algorithm || 'Thompson Sampling',
      explorationRate: status?.exploration_rate || 0.3,
      learningRate: status?.learning_rate || 0.1,
      temperature: status?.temperature || 1.0
    };
  };

  const metrics = getGovernorMetrics();
  const strategy = getGovernorStrategy();

  const getStatusColor = () => {
    if (!governorRunning) return 'bg-muted';
    if (governorStatus === 'ERROR') return 'bg-destructive';
    if (governorStatus === 'LEARNING') return 'bg-warning';
    return 'bg-success';
  };

  const getStatusText = () => {
    if (!governorRunning) return 'Offline';
    return governorStatus || 'Unknown';
  };

  // Calculate recent decision success rate
  const recentDecisions = governorDecisions.slice(0, 10);
  const successfulDecisions = recentDecisions.filter(d => d.executed).length;
  const successRate = recentDecisions.length > 0 
    ? (successfulDecisions / recentDecisions.length * 100).toFixed(1) 
    : 0;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Strategy Governor
            </CardTitle>
            <CardDescription>
              Bayesian decision-making engine with reinforcement learning
            </CardDescription>
          </div>
          <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${governorRunning ? 'animate-pulse' : ''}`} />
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 space-y-6">
        {/* Main Control */}
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
            <div className="flex items-center gap-3">
              <Power className={`w-5 h-5 ${governorRunning ? 'text-success' : 'text-muted-foreground'}`} />
              <div>
                <p className="font-medium">Governor Status</p>
                <p className="text-sm text-muted-foreground">
                  {governorRunning ? 'Making autonomous decisions' : 'Click to activate'}
                </p>
              </div>
            </div>
            <Button
              onClick={handleToggleGovernor}
              variant={governorRunning ? "destructive" : "default"}
              size="sm"
              className="min-w-[100px]"
            >
              {governorRunning ? 'Stop' : 'Start'} Governor
            </Button>
          </div>

          {/* Status Badge */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Current Status</span>
            <Badge variant="outline" className={`${getStatusColor().replace('bg-', 'text-')}`}>
              {getStatusText()}
            </Badge>
          </div>
        </div>

        {/* Enhanced Metrics */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Performance Metrics</h4>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-muted/30 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <Activity className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Q-Table Size</span>
              </div>
              <p className="text-xl font-bold">{qTableSize}</p>
            </div>
            
            <div className="p-3 bg-muted/30 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Success Rate</span>
              </div>
              <p className="text-xl font-bold">{metrics.successRate}%</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-muted/30 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <Target className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Total Decisions</span>
              </div>
              <p className="text-xl font-bold">{metrics.totalDecisions}</p>
            </div>
            
            <div className="p-3 bg-muted/30 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <Zap className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Avg Reward</span>
              </div>
              <p className="text-xl font-bold">{metrics.avgReward}</p>
            </div>
          </div>

          <div className="p-3 bg-muted/30 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted-foreground">Knowledge Growth</span>
              <span className="text-xs font-medium">{kbMetrics.growthRate.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div 
                className="bg-primary h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, kbMetrics.growthRate * 10)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Enhanced: Governor Strategy Information */}
        <div className="space-y-3 pt-3 border-t">
          <h4 className="text-sm font-medium">Strategy Configuration</h4>
          
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Mode:</span>
              <span className="font-mono">{strategy.mode}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Algorithm:</span>
              <span className="font-mono">{strategy.algorithm}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Exploration Rate:</span>
              <span className="font-mono">{(strategy.explorationRate * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Learning Rate:</span>
              <span className="font-mono">{strategy.learningRate}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Temperature:</span>
              <span className="font-mono">{strategy.temperature}</span>
            </div>
          </div>
        </div>

        {/* Enhanced: Decision Type Distribution */}
        {Object.keys(metrics.decisionTypes).length > 0 && (
          <div className="space-y-2 pt-3 border-t">
            <h4 className="text-sm font-medium">Decision Types</h4>
            <div className="space-y-1">
              {Object.entries(metrics.decisionTypes).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between text-xs p-2 bg-muted/20 rounded">
                  <span className="capitalize">{type}</span>
                  <Badge variant="outline" className="text-xs">{count}</Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Auto Learning Toggle */}
        <div className="space-y-3 pt-3 border-t">
          <div className="flex items-center justify-between">
            <Label htmlFor="auto-learning" className="flex flex-col gap-1">
              <span className="font-medium">Auto Learning</span>
              <span className="text-xs text-muted-foreground">
                Enable autonomous knowledge acquisition
              </span>
            </Label>
            <Switch
              id="auto-learning"
              checked={autoLearningConfig.enabled}
              onCheckedChange={handleToggleAutoLearning}
              disabled={!governorRunning}
            />
          </div>

          {autoLearningConfig.enabled && (
            <div className="space-y-2 text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>Exploration Rate</span>
                <span className="font-mono">{getLearningMetrics().explorationRate}%</span>
              </div>
              <div className="flex justify-between">
                <span>Min PFAB Score</span>
                <span className="font-mono">{getLearningMetrics().minPfabScore}</span>
              </div>
              <div className="flex justify-between">
                <span>Min Coverage</span>
                <span className="font-mono">{getLearningMetrics().minCoverage}%</span>
              </div>
              <div className="flex justify-between">
                <span>Loop Interval</span>
                <span className="font-mono">{getLearningMetrics().loopInterval}s</span>
              </div>
              <div className="flex justify-between">
                <span>Bootstrap Threshold</span>
                <span className="font-mono">{getLearningMetrics().bootstrapThreshold}</span>
              </div>
              <div className="flex justify-between">
                <span>Min Growth Rate</span>
                <span className="font-mono">{getLearningMetrics().minGrowthRate}%</span>
              </div>
              <div className="flex justify-between">
                <span>Min LLM Health</span>
                <span className="font-mono">{getLearningMetrics().minLlmHealth}%</span>
              </div>
            </div>
          )}
        </div>

        {/* Recent Decisions */}
        {governorDecisions.length > 0 && (
          <div className="space-y-2 pt-3 border-t">
            <h4 className="text-sm font-medium">Recent Decisions</h4>
            <div className="space-y-1 max-h-[120px] overflow-y-auto">
              {governorDecisions.slice(0, 5).map((decision, idx) => (
                <div key={idx} className="text-xs p-2 bg-muted/20 rounded flex items-center justify-between">
                  <span className="truncate flex-1">{decision.action}</span>
                  <Badge variant={decision.executed ? "default" : "secondary"} className="text-xs ml-2">
                    {decision.executed ? "Done" : "Pending"}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default GovernorControlPanel;