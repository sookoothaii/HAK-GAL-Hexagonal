import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  Target,
  Palette,
  Activity,
  Gauge,
  Layers,
  Package,
  GitBranch,
  Rocket
} from 'lucide-react';
import { cn } from '@/lib/utils';

const LEARNING_PRESETS = {
  conservative: {
    name: 'Conservative',
    description: 'Slow and careful learning, high accuracy',
    icon: Shield,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    settings: {
      loopIntervalSeconds: 30,
      explorationRate: 20,
      minPfabScore: 80,
      bootstrapThreshold: 200,
      parallelInstances: 1,
      batchSize: 10,
      engineDelay: 10
    }
  },
  balanced: {
    name: 'Balanced',
    description: 'Optimal balance of speed and quality',
    icon: Brain,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    settings: {
      loopIntervalSeconds: 15,
      explorationRate: 35,
      minPfabScore: 60,
      bootstrapThreshold: 100,
      parallelInstances: 2,
      batchSize: 20,
      engineDelay: 5
    }
  },
  aggressive: {
    name: 'Aggressive',
    description: 'Fast learning, may include more noise',
    icon: Zap,
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
    settings: {
      loopIntervalSeconds: 5,
      explorationRate: 50,
      minPfabScore: 40,
      bootstrapThreshold: 50,
      parallelInstances: 4,
      batchSize: 30,
      engineDelay: 2
    }
  },
  ultra: {
    name: 'Ultra Performance',
    description: 'Maximum speed for 200+ facts/min',
    icon: Rocket,
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
    settings: {
      loopIntervalSeconds: 3,
      explorationRate: 70,
      minPfabScore: 30,
      bootstrapThreshold: 25,
      parallelInstances: 6,
      batchSize: 50,
      engineDelay: 0
    }
  }
};

const ProSettingsEnhanced: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [selectedPreset, setSelectedPreset] = useState<string>('balanced');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showPerformance, setShowPerformance] = useState(false);
  const [saving, setSaving] = useState(false);
  const [exportingData, setExportingData] = useState(false);
  
  const isConnected = useGovernorStore(state => state.isConnected);
  const autoLearningConfig = useGovernorStore(state => state.autoLearningConfig);
  const kbMetrics = useGovernorStore(state => state.kbMetrics);
  const governorStatus = useGovernorStore(state => state.governorStatus);
  const systemStatus = useGovernorStore(state => state.systemStatus);

  // Performance settings (stored locally for now)
  const [performanceSettings, setPerformanceSettings] = useState({
    parallelInstances: 2,
    batchSize: 20,
    engineDelay: 5,
    bulkApiEnabled: false,
    compressionEnabled: false,
    cacheEnabled: true
  });

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
    
    // Apply preset settings including performance
    wsService.emit('set_learning_parameters', {
      enabled: autoLearningConfig?.enabled ?? true,
      ...presetSettings
    });

    // Update local performance settings
    setPerformanceSettings(prev => ({
      ...prev,
      parallelInstances: presetSettings.parallelInstances,
      batchSize: presetSettings.batchSize,
      engineDelay: presetSettings.engineDelay
    }));

    // Send performance settings to backend
    wsService.emit('set_performance_config', {
      parallelInstances: presetSettings.parallelInstances,
      batchSize: presetSettings.batchSize,
      engineDelay: presetSettings.engineDelay
    });
  };

  const handleAdvancedSetting = (key: string, value: number) => {
    wsService.emit('set_learning_parameters', {
      ...autoLearningConfig,
      [key]: value
    });
  };

  const handlePerformanceSetting = (key: string, value: number | boolean) => {
    const newSettings = {
      ...performanceSettings,
      [key]: value
    };
    setPerformanceSettings(newSettings);
    
    // Send to backend
    wsService.emit('set_performance_config', newSettings);
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

  const getExpectedFactsPerMin = () => {
    const instances = performanceSettings.parallelInstances;
    const batchSize = performanceSettings.batchSize;
    const delay = performanceSettings.engineDelay;
    const interval = autoLearningConfig?.loopIntervalSeconds || 15;
    
    // Rough calculation
    const factsPerCycle = instances * batchSize;
    const cyclesPerMin = Math.max(1, 60 / (interval + delay));
    return Math.round(factsPerCycle * cyclesPerMin * 0.7); // 0.7 for realistic factor
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
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="learning">Learning</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="experimental">Experimental</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="w-5 h-5" />
                Appearance
              </CardTitle>
              <CardDescription>Customize the look and feel</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="space-y-2">
                  <Label>Theme</Label>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <input
                        type="radio"
                        id="light"
                        name="theme"
                        value="light"
                        checked={theme === 'light'}
                        onChange={(e) => handleThemeChange(e.target.value as any)}
                        className="h-4 w-4"
                      />
                      <Label htmlFor="light" className="flex items-center gap-2 cursor-pointer">
                        <Sun className="w-4 h-4" />
                        Light
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="radio"
                        id="dark"
                        name="theme"
                        value="dark"
                        checked={theme === 'dark'}
                        onChange={(e) => handleThemeChange(e.target.value as any)}
                        className="h-4 w-4"
                      />
                      <Label htmlFor="dark" className="flex items-center gap-2 cursor-pointer">
                        <Moon className="w-4 h-4" />
                        Dark
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="radio"
                        id="system"
                        name="theme"
                        value="system"
                        checked={theme === 'system'}
                        onChange={(e) => handleThemeChange(e.target.value as any)}
                        className="h-4 w-4"
                      />
                      <Label htmlFor="system" className="flex items-center gap-2 cursor-pointer">
                        <Monitor className="w-4 h-4" />
                        System
                      </Label>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                Data Management
              </CardTitle>
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
                <span className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  Self-Learning Mode
                </span>
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
                            "cursor-pointer transition-all hover:shadow-md",
                            isSelected && "ring-2 ring-primary shadow-lg",
                            preset.bgColor
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
                            {key === 'ultra' && (
                              <p className="text-xs font-semibold mt-1 text-red-500">
                                ⚡ {preset.settings.parallelInstances} engines × {preset.settings.batchSize} facts
                              </p>
                            )}
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
                    <div className="flex gap-2">
                      <Badge variant="secondary">
                        {kbMetrics?.growthRate || 0} facts/min
                      </Badge>
                      <Badge variant="outline">
                        Expected: ~{getExpectedFactsPerMin()} facts/min
                      </Badge>
                    </div>
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
        </TabsContent>

        {/* Performance Settings */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gauge className="w-5 h-5" />
                Engine Performance Tuning
              </CardTitle>
              <CardDescription>
                Fine-tune engine behavior for maximum fact generation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Performance Controls Toggle */}
              <div className="pt-3 border-t">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPerformance(!showPerformance)}
                  className="w-full"
                >
                  <Rocket className="w-4 h-4 mr-2" />
                  {showPerformance ? 'Hide' : 'Show'} Performance Controls
                </Button>
              </div>

              {showPerformance && (
                <>
                  <Alert className="border-orange-500/50">
                    <Zap className="h-4 w-4 text-orange-500" />
                    <AlertDescription>
                      Higher values increase fact generation speed but may impact system stability.
                      Monitor CPU and memory usage when using aggressive settings.
                    </AlertDescription>
                  </Alert>

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <div>
                          <Label>Parallel Engine Instances</Label>
                          <p className="text-xs text-muted-foreground">
                            Number of engines running simultaneously
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">
                            {performanceSettings.parallelInstances}
                          </span>
                          <Badge variant={performanceSettings.parallelInstances > 4 ? "destructive" : "secondary"}>
                            {performanceSettings.parallelInstances > 4 ? 'Extreme' : 'Normal'}
                          </Badge>
                        </div>
                      </div>
                      <Slider
                        value={[performanceSettings.parallelInstances]}
                        onValueChange={([value]) => handlePerformanceSetting('parallelInstances', value)}
                        min={1}
                        max={8}
                        step={1}
                        className="w-full"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <div>
                          <Label>Batch Size</Label>
                          <p className="text-xs text-muted-foreground">
                            Facts processed per API call
                          </p>
                        </div>
                        <span className="text-sm font-medium">
                          {performanceSettings.batchSize} facts
                        </span>
                      </div>
                      <Slider
                        value={[performanceSettings.batchSize]}
                        onValueChange={([value]) => handlePerformanceSetting('batchSize', value)}
                        min={5}
                        max={100}
                        step={5}
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <div>
                          <Label>Engine Delay</Label>
                          <p className="text-xs text-muted-foreground">
                            Pause between fact generation cycles
                          </p>
                        </div>
                        <span className="text-sm font-medium">
                          {performanceSettings.engineDelay}s
                        </span>
                      </div>
                      <Slider
                        value={[performanceSettings.engineDelay]}
                        onValueChange={([value]) => handlePerformanceSetting('engineDelay', value)}
                        min={0}
                        max={20}
                        step={1}
                      />
                    </div>
                  </div>

                  <div className="space-y-3 pt-4 border-t">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Bulk API Mode</Label>
                        <p className="text-sm text-muted-foreground">
                          Send multiple facts in single request
                        </p>
                      </div>
                      <Switch 
                        checked={performanceSettings.bulkApiEnabled}
                        onCheckedChange={(checked) => handlePerformanceSetting('bulkApiEnabled', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Response Compression</Label>
                        <p className="text-sm text-muted-foreground">
                          Compress API responses for faster transfer
                        </p>
                      </div>
                      <Switch 
                        checked={performanceSettings.compressionEnabled}
                        onCheckedChange={(checked) => handlePerformanceSetting('compressionEnabled', checked)}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Smart Caching</Label>
                        <p className="text-sm text-muted-foreground">
                          Cache frequent queries and responses
                        </p>
                      </div>
                      <Switch 
                        checked={performanceSettings.cacheEnabled}
                        onCheckedChange={(checked) => handlePerformanceSetting('cacheEnabled', checked)}
                      />
                    </div>
                  </div>
                </>
              )}

              {/* Performance Metrics */}
              <div className="space-y-3 pt-4 border-t">
                <h4 className="text-sm font-medium flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  Performance Metrics
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-1">
                    <p className="text-muted-foreground">Expected Facts/Min</p>
                    <p className="text-2xl font-bold">{getExpectedFactsPerMin()}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-muted-foreground">Actual Facts/Min</p>
                    <p className="text-2xl font-bold">{kbMetrics?.growthRate?.toFixed(0) || 0}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-muted-foreground">Efficiency</p>
                    <p className="text-lg font-medium">
                      {kbMetrics?.growthRate && getExpectedFactsPerMin() > 0
                        ? Math.round((kbMetrics.growthRate / getExpectedFactsPerMin()) * 100)
                        : 0}%
                    </p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-muted-foreground">Total Facts</p>
                    <p className="text-lg font-medium">{kbMetrics?.factCount || 0}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Resource Usage
              </CardTitle>
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
        </TabsContent>

        {/* Experimental Settings */}
        <TabsContent value="experimental" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                Experimental Features
              </CardTitle>
              <CardDescription>
                Cutting-edge features that may be unstable
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert className="border-purple-500/50">
                <Sparkles className="h-4 w-4 text-purple-500" />
                <AlertDescription>
                  These features are experimental and may cause unexpected behavior.
                  Enable at your own risk.
                </AlertDescription>
              </Alert>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Multi-Threading</Label>
                    <p className="text-sm text-muted-foreground">
                      Process facts in parallel threads
                    </p>
                  </div>
                  <Switch />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Predictive Loading</Label>
                    <p className="text-sm text-muted-foreground">
                      Pre-load likely topics before processing
                    </p>
                  </div>
                  <Switch />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Neural Deduplication</Label>
                    <p className="text-sm text-muted-foreground">
                      Use ML to detect semantic duplicates
                    </p>
                  </div>
                  <Switch />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Quantum Random Sampling</Label>
                    <p className="text-sm text-muted-foreground">
                      Use quantum RNG for topic selection
                    </p>
                  </div>
                  <Switch disabled />
                </div>
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
                  <p className="font-mono">2025.08.04</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Backend</p>
                  <p className="font-mono text-xs">/api</p>
                </div>
                <div>
                  <p className="text-muted-foreground">WebSocket</p>
                  <p className="font-mono text-xs">/socket.io</p>
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

export default ProSettingsEnhanced;
