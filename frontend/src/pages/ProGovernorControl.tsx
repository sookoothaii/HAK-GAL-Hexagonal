import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { Brain, Cpu, Zap, Play, Pause, BarChart3, Activity, Settings, Sparkles } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiService from '@/services/apiService';
import wsService from '@/services/websocket';
import { toast } from 'sonner';

const ProGovernorControl: React.FC = () => {
  const store = useGovernorStore();
  const [isStarting, setIsStarting] = useState(false);
  const [autoMode, setAutoMode] = useState(true);
  const [loopInterval, setLoopInterval] = useState(10);
  const [bootstrapThreshold, setBootstrapThreshold] = useState(100);
  
  // Get governor state from store
  const governorRunning = store.governor?.running || false;
  const governorStatus = store.governor?.status || 'idle';
  const decisions = store.governor?.decisions || [];
  const rewardHistory = store.governor?.rewardHistory || [];
  const learningRate = store.kb?.metrics?.growthRate || 0;
  const factCount = store.kb?.metrics?.factCount || 0;
  
  const handleToggleGovernor = async () => {
    setIsStarting(true);
    try {
      if (governorRunning) {
        // Stop governor
        const response = await apiService.stopGovernor();
        if (response.success) {
          toast.success('Governor stopped');
          wsService.emit('governor_control', { action: 'stop' });
        }
      } else {
        // Start governor
        const response = await apiService.startGovernor();
        if (response.success) {
          toast.success('Governor started');
          wsService.emit('governor_control', { action: 'start' });
        }
      }
    } catch (error) {
      console.error('Error controlling governor:', error);
      toast.error('Failed to control governor');
    } finally {
      setIsStarting(false);
    }
  };
  
  const handleUpdateConfig = async () => {
    try {
      const config = {
        enabled: autoMode,
        loopIntervalSeconds: loopInterval,
        bootstrapThreshold: bootstrapThreshold
      };
      
      wsService.emit('update_auto_learning_config', config);
      toast.success('Configuration updated');
    } catch (error) {
      console.error('Error updating config:', error);
      toast.error('Failed to update configuration');
    }
  };
  
  // Calculate average reward
  const avgReward = rewardHistory.length > 0
    ? (rewardHistory.reduce((sum, r) => sum + r.value, 0) / rewardHistory.length).toFixed(3)
    : '0.000';
  
  return (
    <div className="h-full overflow-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Cpu className="w-6 h-6 text-primary" />
          Neurosymbolic Governor Control
        </h1>
        <p className="text-muted-foreground mt-1">
          Orchestrates learning through neural-symbolic integration and constitutional compliance
        </p>
      </div>
      
      {/* Main Control Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Governor Status
            </span>
            <Badge variant={governorRunning ? 'default' : 'secondary'}>
              {governorRunning ? 'RUNNING' : 'STOPPED'}
            </Badge>
          </CardTitle>
          <CardDescription>
            Coordinates neural reasoning, symbolic provers, and human verification for intelligent knowledge expansion
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Status</Label>
              <div className="flex items-center gap-2">
                {governorRunning ? (
                  <Activity className="w-4 h-4 text-green-500 animate-pulse" />
                ) : (
                  <Activity className="w-4 h-4 text-muted-foreground" />
                )}
                <span className="text-sm font-medium">{governorStatus}</span>
              </div>
            </div>
            
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Learning Rate</Label>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-yellow-500" />
                <span className="text-sm font-medium">{learningRate.toFixed(1)} facts/min</span>
              </div>
            </div>
            
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Total Facts</Label>
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-blue-500" />
                <span className="text-sm font-medium">{factCount.toLocaleString()}</span>
              </div>
            </div>
            
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Avg Reward</Label>
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-purple-500" />
                <span className="text-sm font-medium">{avgReward}</span>
              </div>
            </div>
          </div>
          
          <Button
            onClick={handleToggleGovernor}
            disabled={isStarting}
            className="w-full"
            variant={governorRunning ? 'destructive' : 'default'}
          >
            {isStarting ? (
              <>
                <Activity className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : governorRunning ? (
              <>
                <Pause className="w-4 h-4 mr-2" />
                Stop Governor
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start Governor
              </>
            )}
          </Button>
        </CardContent>
      </Card>
      
      {/* Configuration Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Learning Configuration
          </CardTitle>
          <CardDescription>
            Fine-tune the autonomous learning parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Auto Mode Toggle */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto-mode">Automatic Topic Selection</Label>
              <p className="text-xs text-muted-foreground">
                Let the governor choose topics autonomously
              </p>
            </div>
            <Switch
              id="auto-mode"
              checked={autoMode}
              onCheckedChange={setAutoMode}
            />
          </div>
          
          {/* Loop Interval */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="loop-interval">Loop Interval</Label>
              <span className="text-sm text-muted-foreground">{loopInterval}s</span>
            </div>
            <Slider
              id="loop-interval"
              min={5}
              max={60}
              step={5}
              value={[loopInterval]}
              onValueChange={(value) => setLoopInterval(value[0])}
            />
            <p className="text-xs text-muted-foreground">
              Time between governor decision cycles
            </p>
          </div>
          
          {/* Bootstrap Threshold */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="bootstrap-threshold">Bootstrap Threshold</Label>
              <span className="text-sm text-muted-foreground">{bootstrapThreshold}</span>
            </div>
            <Slider
              id="bootstrap-threshold"
              min={50}
              max={500}
              step={50}
              value={[bootstrapThreshold]}
              onValueChange={(value) => setBootstrapThreshold(value[0])}
            />
            <p className="text-xs text-muted-foreground">
              Minimum facts before advanced strategies
            </p>
          </div>
          
          <Button onClick={handleUpdateConfig} className="w-full">
            Apply Configuration
          </Button>
        </CardContent>
      </Card>
      
      {/* Recent Decisions */}
      {decisions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5" />
              Recent Decisions
            </CardTitle>
            <CardDescription>
              Last {Math.min(5, decisions.length)} governor actions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {decisions.slice(0, 5).map((decision, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{decision.type}</Badge>
                    <span className="text-sm">{decision.action}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(decision.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Info Alert */}
      <Alert className="mt-6">
        <Brain className="w-4 h-4" />
        <AlertDescription>
          The Neurosymbolic Governor orchestrates the HAK-GAL Suite's learning processes by combining:
          <br />• <strong>Neural reasoning</strong> from the HRM model for confidence assessment
          <br />• <strong>Symbolic verification</strong> through logical provers
          <br />• <strong>Constitutional compliance</strong> with HAK/GAL principles (Articles 1-8)
          <br />• <strong>Adaptive scheduling</strong> based on knowledge graph topology and learning velocity
          <br />
          It decides when to activate knowledge generation engines based on semantic coverage gaps,
          reasoning uncertainty metrics, and human-verified trust scores.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default ProGovernorControl;
