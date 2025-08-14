import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Slider } from '@/components/ui/slider';
import { useGovernorStore } from '@/stores/useGovernorStore';
import wsService from '@/services/websocket';
import {
  Sun,
  Moon,
  Monitor,
  Zap,
  Brain,
  Gauge,
  Shield,
  Sparkles,
  Info,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Cpu,
  Database,
  Network,
  Bot,
  Settings2,
  RefreshCw,
  Download,
  Upload,
  Loader2,
  TrendingUp,
  Target
} from 'lucide-react';
import { cn } from '@/lib/utils';

const LEARNING_PRESETS = {
  conservative: {
    name: 'Conservative',
    description: 'Slow and careful learning, high accuracy',
    icon: Shield,
    color: 'text-blue-500',
    settings: {
      loopIntervalSeconds: 30,
      explorationRate: 20,
      minPfabScore: 80,
      bootstrapThreshold: 200
    }
  },
  balanced: {
    name: 'Balanced',
    description: 'Optimal balance of speed and quality',
    icon: Brain,
    color: 'text-purple-500',
    settings: {
      loopIntervalSeconds: 15,
      explorationRate: 35,
      minPfabScore: 60,
      bootstrapThreshold: 100
    }
  },
  aggressive: {
    name: 'Aggressive',
    description: 'Fast learning, may include more noise',
    icon: Zap,
    color: 'text-orange-500',
    settings: {
      loopIntervalSeconds: 5,
      explorationRate: 50,
      minPfabScore: 40,
      bootstrapThreshold: 50
    }
  },
  experimental: {
    name: 'Experimental',
    description: 'Maximum exploration, research mode',
    icon: Sparkles,
    color: 'text-pink-500',
    settings: {
      loopIntervalSeconds: 3,
      explorationRate: 70,
      minPfabScore: 20,
      bootstrapThreshold: 25
    }
  }
};

const Settings: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [selectedPreset, setSelectedPreset] = useState<string>('balanced');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [saving, setSaving] = useState(false);
  const [exportingData, setExportingData] = useState(false);
  
  const isConnected = useGovernorStore(state => state.isConnected);
  const autoLearningConfig = useGovernorStore(state => state.autoLearningConfig);
  const kbMetrics = useGovernorStore(state => state.kbMetrics);
  const governorStatus = useGovernorStore(state => state.governorStatus);
  const systemStatus = useGovernorStore(state => state.systemStatus);

  // Theme handling
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system' | null;
    if (savedTheme) {
      setTheme(savedTheme);
      applyTheme(savedTheme);
    }
  }, []);

  const applyTheme = (newTheme: 'light' | 'dark' | 'system') => {
    const root = window.document.documentElement;
    if (newTheme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.toggle('dark', systemTheme === 'dark');
    } else {
      root.classList.toggle('dark', newTheme === 'dark');
    }
    localStorage.setItem('theme', newTheme);
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    applyTheme(newTheme);
  };

  const handlePresetChange = (preset: string) => {
    setSelectedPreset(preset);
    const presetSettings = LEARNING_PRESETS[preset as keyof typeof LEARNING_PRESETS].settings;
    
    // Apply preset settings
    wsService.emit('set_learning_parameters', {
      enabled: autoLearningConfig?.enabled ?? true,
      ...presetSettings
    });
  };

  const handleAdvancedSetting = (key: string, value: number) => {
    wsService.emit('set_learning_parameters', {
      ...autoLearningConfig,
      [key]: value
    });
  };

  const handleToggleLearning = () => {
    wsService.emit('toggle_auto_learning');
  };

  const handleExportKnowledge = async () => {
    setExportingData(true);
    try {
      const { API_BASE_URL } = await import('@/config/backends');
      const response = await fetch(`${API_BASE_URL}/api/knowledge-base/raw`);
      const data = await response.json();
      
      // Create download
      const blob = new Blob([JSON.stringify(data.facts, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `knowledge_base_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExportingData(false);
    }
  };

  const getLearningSpeedDescription = () => {
    const interval = autoLearningConfig?.loopIntervalSeconds || 15;
    if (interval <= 5) return 'Very Fast';
    if (interval <= 10) return 'Fast';
    if (interval <= 20) return 'Moderate';
    if (interval <= 30) return 'Slow';
    return 'Very Slow';
  };

  const getQualityDescription = () => {
    const score = autoLearningConfig?.minPfabScore || 60;
    if (score >= 80) return 'Very High';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Medium';
    if (score >= 20) return 'Low';
    return 'Very Low';
  };

  return (
    <div className="h-full p-6 space-y-6 overflow-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">System Settings</h1>
        <p className="text-muted-foreground mt-1">
          Configure your HAK-GAL knowledge assistant
        </p>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="learning">Learning</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Appearance</CardTitle>
              <CardDescription>Customize the look and feel</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Theme</Label>
                <RadioGroup value={theme} onValueChange={handleThemeChange}>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="light" id="light" />
                    <Label htmlFor="light" className="flex items-center gap-2 cursor-pointer">
                      <Sun className="w-4 h-4" />
                      Light
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="dark" id="dark" />
                    <Label htmlFor="dark" className="flex items-center gap-2 cursor-pointer">
                      <Moon className="w-4 h-4" />
                      Dark
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="system" id="system" />
                    <Label htmlFor="system" className="flex items-center gap-2 cursor-pointer">
                      <Monitor className="w-4 h-4" />
                      System
                    </Label>
                  </div>
                </RadioGroup>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Data Management</CardTitle>
              <CardDescription>Export and backup your knowledge base</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Export Knowledge Base</p>
                  <p className="text-sm text-muted-foreground">
                    Download all {kbMetrics?.factCount || 0} facts as JSON
                  </p>
                </div>
                <Button onClick={handleExportKnowledge} disabled={exportingData}>
                  {exportingData ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Exporting...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      Export
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Learning Settings */}
        <TabsContent value="learning" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Self-Learning Mode</span>
                <Switch
                  checked={autoLearningConfig?.enabled ?? false}
                  onCheckedChange={handleToggleLearning}
                />
              </CardTitle>
              <CardDescription>
                Autonomous knowledge generation and hypothesis testing
              </CardDescription>
            </CardHeader>
            {autoLearningConfig?.enabled && (
              <CardContent className="space-y-6">
                {/* Learning Presets */}
                <div className="space-y-3">
                  <Label>Learning Strategy</Label>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(LEARNING_PRESETS).map(([key, preset]) => {
                      const Icon = preset.icon;
                      const isSelected = selectedPreset === key;
                      return (
                        <Card
                          key={key}
                          className={cn(
                            "cursor-pointer transition-all",
                            isSelected && "ring-2 ring-primary"
                          )}
                          onClick={() => handlePresetChange(key)}
                        >
                          <CardHeader className="pb-3">
                            <CardTitle className="text-sm flex items-center gap-2">
                              <Icon className={cn("w-4 h-4", preset.color)} />
                              {preset.name}
                              {isSelected && <CheckCircle2 className="w-4 h-4 ml-auto text-primary" />}
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-xs text-muted-foreground">
                              {preset.description}
                            </p>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </div>

                {/* Current Performance */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Current Performance</Label>
                    <Badge variant="secondary">
                      {kbMetrics?.growthRate || 0} facts/min
                    </Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Learning Speed:</span>
                      <span className="font-medium">{getLearningSpeedDescription()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Quality Filter:</span>
                      <span className="font-medium">{getQualityDescription()}</span>
                    </div>
                  </div>
                </div>

                {/* Advanced Settings Toggle */}
                <div className="pt-3 border-t">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="w-full"
                  >
                    <Settings2 className="w-4 h-4 mr-2" />
                    {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
                  </Button>
                </div>

                {/* Advanced Settings */}
                {showAdvanced && (
                  <div className="space-y-4 pt-3">
                    <Alert>
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        Advanced settings can significantly impact system behavior. 
                        Use presets unless you understand the implications.
                      </AlertDescription>
                    </Alert>

                    <div className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <Label>Loop Interval</Label>
                          <span className="text-sm text-muted-foreground">
                            {autoLearningConfig?.loopIntervalSeconds}s
                          </span>
                        </div>
                        <Slider
                          value={[autoLearningConfig?.loopIntervalSeconds || 15]}
                          onValueChange={([value]) => handleAdvancedSetting('loopIntervalSeconds', value)}
                          min={1}
                          max={60}
                          step={1}
                        />
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <Label>Exploration Rate</Label>
                          <span className="text-sm text-muted-foreground">
                            {autoLearningConfig?.explorationRate}%
                          </span>
                        </div>
                        <Slider
                          value={[autoLearningConfig?.explorationRate || 30]}
                          onValueChange={([value]) => handleAdvancedSetting('explorationRate', value)}
                          min={0}
                          max={100}
                          step={5}
                        />
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <Label>Quality Threshold</Label>
                          <span className="text-sm text-muted-foreground">
                            {autoLearningConfig?.minPfabScore}%
                          </span>
                        </div>
                        <Slider
                          value={[autoLearningConfig?.minPfabScore || 60]}
                          onValueChange={([value]) => handleAdvancedSetting('minPfabScore', value)}
                          min={0}
                          max={100}
                          step={5}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            )}
          </Card>

          {/* Learning Health Status */}
          <Card>
            <CardHeader>
              <CardTitle>Learning Health</CardTitle>
              <CardDescription>Monitor for optimal performance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bot className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm">Governor Status</span>
                </div>
                {governorStatus?.isRunning ? (
                  <Badge variant="default" className="bg-green-500">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Active
                  </Badge>
                ) : (
                  <Badge variant="secondary">
                    <XCircle className="w-3 h-3 mr-1" />
                    Inactive
                  </Badge>
                )}
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm">Reward Balance</span>
                </div>
                <div className="text-sm">
                  <span className="text-muted-foreground">E:</span> {((governorStatus?.explorationRatio || 0.5) * 100).toFixed(0)}% 
                  <span className="text-muted-foreground mx-1">/</span>
                  <span className="text-muted-foreground">X:</span> {((1 - (governorStatus?.explorationRatio || 0.5)) * 100).toFixed(0)}%
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm">Growth Rate</span>
                </div>
                <span className="text-sm font-medium">
                  {kbMetrics?.growthRate?.toFixed(1) || 0} facts/min
                </span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Settings */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Resource Usage</CardTitle>
              <CardDescription>Monitor system resource consumption</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm flex items-center gap-2">
                      <Cpu className="w-4 h-4" />
                      CPU Usage
                    </span>
                    <span className="text-sm font-medium">
                      {systemStatus?.cpuUsage || 0}%
                    </span>
                  </div>
                  <Progress value={systemStatus?.cpuUsage || 0} className="h-2" />
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm flex items-center gap-2">
                      <Database className="w-4 h-4" />
                      Memory Usage
                    </span>
                    <span className="text-sm font-medium">
                      {systemStatus?.memoryUsage || 0}%
                    </span>
                  </div>
                  <Progress value={systemStatus?.memoryUsage || 0} className="h-2" />
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm flex items-center gap-2">
                      <Network className="w-4 h-4" />
                      Network Latency
                    </span>
                    <span className="text-sm font-medium">
                      {systemStatus?.networkLatency || 0}ms
                    </span>
                  </div>
                  <Progress 
                    value={Math.min((systemStatus?.networkLatency || 0) / 200 * 100, 100)} 
                    className="h-2" 
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Optimization</CardTitle>
              <CardDescription>Improve system performance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Performance optimizations may temporarily affect learning accuracy.
                </AlertDescription>
              </Alert>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Enable GPU Acceleration</Label>
                  <p className="text-sm text-muted-foreground">
                    Use GPU for faster processing
                  </p>
                </div>
                <Switch />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Background Processing</Label>
                  <p className="text-sm text-muted-foreground">
                    Continue learning when minimized
                  </p>
                </div>
                <Switch defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* System Information */}
        <TabsContent value="system" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Information</CardTitle>
              <CardDescription>Technical details and diagnostics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Version</p>
                  <p className="font-mono">2.0.0</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Build</p>
                  <p className="font-mono">2025.08.02</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Backend URL</p>
                  <p className="font-mono text-xs">http://localhost:5001</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Frontend URL</p>
                  <p className="font-mono text-xs">http://localhost:5173</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Knowledge Base</p>
                  <p className="font-mono">{kbMetrics?.factCount || 0} facts</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Connection</p>
                  <Badge variant={isConnected ? "default" : "secondary"}>
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Diagnostics</CardTitle>
              <CardDescription>System health and troubleshooting</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full" onClick={() => window.location.reload()}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Restart Application
              </Button>
              <Button variant="outline" className="w-full">
                <Download className="w-4 h-4 mr-2" />
                Download Logs
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Settings;
