import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useGovernorStore } from '@/stores/useGovernorStore';
import { useGovernorSocket } from '@/hooks/useGovernorSocket';
import { Link } from 'react-router-dom';
import apiService from '@/services/apiService';
import {
  Brain,
  Zap,
  TrendingUp,
  Activity,
  Bot,
  Sparkles,
  ArrowRight,
  Play,
  Pause,
  RefreshCw,
  Target,
  BookOpen,
  MessageSquare,
  Settings,
  BarChart3,
  Rocket,
  CheckCircle2,
  AlertCircle,
  Clock,
  Cpu,
  Database,
  Network,
  Trophy,
  Star,
  Flame
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { cn } from '@/lib/utils';

// Use store history for growth chart
const generateGrowthData = (currentFacts: number, systemLoadHistory: any[], growthRate: number) => {
  // If we have real history, use it
  if (systemLoadHistory && systemLoadHistory.length > 0) {
    return systemLoadHistory.slice(-12).map((item, index) => ({
      time: index === systemLoadHistory.length - 1 ? 'Now' : item.time,
      facts: currentFacts - (systemLoadHistory.length - 1 - index) * Math.max(1, growthRate)
    }));
  }
  // Otherwise show single point
  return [{ time: 'Now', facts: currentFacts }];
};

// Replace achievements with scientific KB Quality metrics (populated from API)
type QualityMetrics = {
  total: number;
  checked: number;
  invalid: number;
  duplicates: number;
  isolated: number;
  contradictions: number;
};

const Dashboard: React.FC = () => {
  const wsService = useGovernorSocket();
  const isConnected = useGovernorStore(state => state.isConnected);
  
  // Request initial data on mount if needed
  useEffect(() => {
    const checkAndRequestData = () => {
      const state = useGovernorStore.getState();
      if (state.isConnected && state.kb.metrics.factCount === 0) {
        console.log('📊 Dashboard mounted - requesting fresh data...');
        wsService.emit('request_initial_data');
      }
    };
    
    // Check immediately
    checkAndRequestData();
    
    // Also check after a short delay in case connection is still establishing
    const timer = setTimeout(checkAndRequestData, 1000);
    
    return () => clearTimeout(timer);
  }, [wsService]);
  const kbMetrics = useGovernorStore(state => state.kb.metrics);
  // Remove duplicate governorStatus, use direct store access
  const autoLearningConfig = useGovernorStore(state => state.autoLearningConfig);
  const engines = useGovernorStore(state => state.engines);
  const llmProviders = useGovernorStore(state => state.llmProviders);
  const knowledgeCategories = useGovernorStore(state => state.kb.categories);
  const systemStatus = useGovernorStore(state => state.systemStatus);
  const systemLoad = useGovernorStore(state => state.systemLoad);

  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('6h');
  const [selectedMetric, setSelectedMetric] = useState<'facts' | 'quality' | 'speed'>('facts');
  const [quality, setQuality] = useState<QualityMetrics | null>(null);
  const [topPreds, setTopPreds] = useState<Array<{ predicate: string; count: number }>>([]);

  const factCount = kbMetrics?.factCount || 0;
  const growthRate = kbMetrics?.growthRate || 0;
  const governorRunning = useGovernorStore(state => state.governor.running);
  const isLearning = autoLearningConfig?.enabled && governorRunning;

  // Fetch KB quality + top predicates on mount
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const q = await apiService.qualityMetrics(3000);
        const p = await apiService.topPredicates(6, 3000);
        if (mounted) {
          setQuality(q?.error ? null : q);
          setTopPreds(Array.isArray(p?.top_predicates) ? p.top_predicates : []);
        }
      } catch {}
    })();
    return () => { mounted = false; };
  }, []);

  // Calculate system health score
  const healthScore = (() => {
    let score = 100;
    if (!isConnected) score -= 50;
    if (!governorRunning) score -= 20;
    if (growthRate < 1) score -= 10;
    if (systemLoad?.cpu > 80) score -= 10;
    if (systemLoad?.memory > 80) score -= 10;
    return Math.max(0, score);
  })();

  const handleToggleLearning = () => {
    if (isLearning) {
      wsService.emit('governor_control', { action: 'stop' });
    } else {
      wsService.emit('governor_control', { action: 'start' });
    }
  };

  const systemLoadHistory = useGovernorStore(state => state.systemLoadHistory);
  const growthData = generateGrowthData(factCount, systemLoadHistory, growthRate);

  const engineStatusData = engines.map(engine => ({
    name: engine.name,
    value: engine.status === 'running' ? 1 : 0,
    status: engine.status
  }));

  const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b'];

  if (!isConnected) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-500" />
              Connection Lost
            </CardTitle>
            <CardDescription>
              Unable to connect to the HAK-GAL backend
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => window.location.reload()} className="w-full">
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry Connection
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-full p-6 space-y-6 overflow-auto">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 p-8 text-white">
        <div className="relative z-10">
          <h1 className="text-4xl font-bold mb-2">Welcome to HAK-GAL</h1>
          <p className="text-xl opacity-90 mb-6">
            {factCount > 0 ? `Your autonomous knowledge assistant has collected ${factCount.toLocaleString()} facts` : 'Starting up autonomous knowledge assistant...'}
          </p>
          <div className="flex items-center gap-4">
            <Button 
              size="lg" 
              variant={isLearning ? "secondary" : "default"}
              onClick={handleToggleLearning}
              className={cn(
                "font-semibold",
                isLearning && "bg-white/20 hover:bg-white/30 text-white"
              )}
            >
              {isLearning ? (
                <>
                  <Pause className="w-5 h-5 mr-2" />
                  Pause Learning
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  Start Learning
                </>
              )}
            </Button>
            <Link to="/command-center">
              <Button size="lg" variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                <MessageSquare className="w-5 h-5 mr-2" />
                Ask Questions
              </Button>
            </Link>
          </div>
        </div>
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Database className="w-4 h-4" />
              Total Knowledge
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{factCount > 0 ? factCount.toLocaleString() : '...'}</div>
            <p className="text-xs text-muted-foreground mt-1">
              <TrendingUp className="w-3 h-3 inline mr-1" />
              +{Math.floor(growthRate * 60)} today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Learning Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{growthRate > 0 ? growthRate.toFixed(1) : '0.0'}</div>
            <p className="text-xs text-muted-foreground mt-1">facts per minute</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Activity className="w-4 h-4" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold">{healthScore}%</div>
              {healthScore >= 80 ? (
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              ) : healthScore >= 50 ? (
                <AlertCircle className="w-5 h-5 text-yellow-500" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-500" />
              )}
            </div>
            <Progress value={healthScore} className="h-1 mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              KB Quality
            </CardTitle>
          </CardHeader>
          <CardContent>
            {quality ? (
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center justify-between"><span>Checked</span><span className="font-medium">{quality.checked}</span></div>
                <div className="flex items-center justify-between"><span>Invalid</span><span className="font-medium">{quality.invalid}</span></div>
                <div className="flex items-center justify-between"><span>Duplicates</span><span className="font-medium">{quality.duplicates}</span></div>
                <div className="flex items-center justify-between"><span>Contradictions</span><span className="font-medium">{quality.contradictions}</span></div>
              </div>
            ) : (
              <div className="text-xs text-muted-foreground">Loading metrics…</div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="learning">Learning Status</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="quickstart">Quick Start</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Knowledge Growth Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Knowledge Growth</CardTitle>
                <CardDescription>Facts accumulated over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={growthData}>
                    <defs>
                      <linearGradient id="colorFacts" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area 
                      type="monotone" 
                      dataKey="facts" 
                      stroke="#8b5cf6" 
                      fillOpacity={1} 
                      fill="url(#colorFacts)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Learning Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Top Predicates</CardTitle>
                <CardDescription>Most frequent predicates in KB</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {topPreds.length > 0 ? (
                    topPreds.map((p, i) => (
                      <div key={i} className="flex items-center justify-between text-sm">
                        <span className="font-mono">{p.predicate}</span>
                        <Badge variant="outline">{p.count}</Badge>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-muted-foreground">Loading…</div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and navigation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Link to="/command-center">
                  <Button variant="outline" className="w-full h-20 flex-col gap-2">
                    <MessageSquare className="w-5 h-5" />
                    <span className="text-xs">Ask AI</span>
                  </Button>
                </Link>
                <Link to="/knowledge-stats">
                  <Button variant="outline" className="w-full h-20 flex-col gap-2">
                    <BarChart3 className="w-5 h-5" />
                    <span className="text-xs">Analytics</span>
                  </Button>
                </Link>
                <Link to="/auto-learning">
                  <Button variant="outline" className="w-full h-20 flex-col gap-2">
                    <Brain className="w-5 h-5" />
                    <span className="text-xs">Learning</span>
                  </Button>
                </Link>
                <Link to="/settings">
                  <Button variant="outline" className="w-full h-20 flex-col gap-2">
                    <Settings className="w-5 h-5" />
                    <span className="text-xs">Settings</span>
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Learning Status Tab */}
        <TabsContent value="learning" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Governor Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Governor Status</span>
                  <Badge variant={governorRunning ? 'default' : 'secondary'}>
                  {governorRunning ? 'Active' : 'Inactive'}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Total Decisions</span>
                    <span className="font-medium">{useGovernorStore(state => state.governor.decisions).length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Governor Status</span>
                    <span className="font-medium">
                    {useGovernorStore(state => state.governor.status)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Reward History</span>
                    <span className="font-medium">{useGovernorStore(state => state.governor.rewardHistory).length} points</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* LLM Providers */}
            <Card>
              <CardHeader>
                <CardTitle>AI Providers</CardTitle>
                <CardDescription>Connected language models</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {llmProviders.map((provider) => (
                  <div key={provider.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                  <div className={cn(
                  "w-2 h-2 rounded-full",
                  provider.status === 'online' ? "bg-green-500" : "bg-red-500"
                  )} />
                  <span className="text-sm font-medium">{provider.name}</span>
                  </div>
                  <Badge variant="outline" className="text-xs">
                  {provider.model}
                  </Badge>
                  </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Learning Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Active Learning Configuration</CardTitle>
              <CardDescription>Current parameters and settings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Loop Interval</p>
                  <p className="font-medium">{autoLearningConfig?.loopIntervalSeconds || 15}s</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Quality Threshold</p>
                  <p className="font-medium">{autoLearningConfig?.minPfabScore || 60}%</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Exploration Rate</p>
                  <p className="font-medium">{autoLearningConfig?.explorationRate || 30}%</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Bootstrap Threshold</p>
                  <p className="font-medium">{autoLearningConfig?.bootstrapThreshold || 100}</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t">
                <Link to="/settings?tab=learning">
                  <Button variant="outline" size="sm" className="w-full">
                    Adjust Learning Settings
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Cpu className="w-4 h-4" />
                  CPU Usage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemLoad?.cpu || 0}%</div>
                <Progress value={systemLoad?.cpu || 0} className="h-2 mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Database className="w-4 h-4" />
                  Memory Usage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemLoad?.memory || 0}%</div>
                <Progress value={systemLoad?.memory || 0} className="h-2 mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Network className="w-4 h-4" />
                  Network Latency
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{systemStatus?.networkLatency || 0}ms</div>
                <Progress 
                  value={Math.min((systemStatus?.networkLatency || 0) / 200 * 100, 100)} 
                  className="h-2 mt-2" 
                />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>System Recommendations</CardTitle>
              <CardDescription>Optimization suggestions based on current performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {systemLoad?.cpu > 80 && (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      High CPU usage detected. Consider reducing learning frequency.
                    </AlertDescription>
                  </Alert>
                )}
                {systemLoad?.memory > 80 && (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      High memory usage. Knowledge base may need optimization.
                    </AlertDescription>
                  </Alert>
                )}
                {growthRate < 1 && autoLearningConfig?.enabled && (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      Low learning rate detected. Try increasing exploration rate.
                    </AlertDescription>
                  </Alert>
                )}
                {(!systemLoad?.cpu || systemLoad?.cpu < 80) && 
                 (!systemLoad?.memory || systemLoad?.memory < 80) && 
                 growthRate >= 1 && (
                  <Alert className="border-green-500 bg-green-500/10">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <AlertDescription className="text-green-700 dark:text-green-300">
                      System performance is optimal. No issues detected.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Quick Start Tab */}
        <TabsContent value="quickstart" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Getting Started with HAK-GAL</CardTitle>
              <CardDescription>Learn how to make the most of your AI assistant</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold">1</span>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Enable Auto-Learning</h3>
                    <p className="text-sm text-muted-foreground">
                      Click the "Start Learning" button to begin autonomous knowledge generation.
                      The system will continuously discover and validate new facts.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold">2</span>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Ask Questions</h3>
                    <p className="text-sm text-muted-foreground">
                      Navigate to the Command Center to query the knowledge base. 
                      Ask anything from simple facts to complex reasoning tasks.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold">3</span>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Monitor Progress</h3>
                    <p className="text-sm text-muted-foreground">
                      Use the Analytics page to track knowledge growth, identify patterns,
                      and ensure the system is learning effectively.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold">4</span>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">Optimize Settings</h3>
                    <p className="text-sm text-muted-foreground">
                      Choose a learning strategy in Settings that matches your needs:
                      Conservative for accuracy, or Aggressive for rapid growth.
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <div className="flex gap-3">
                  <Link to="/command-center">
                    <Button>
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Try Command Center
                    </Button>
                  </Link>
                  <Link to="/settings">
                    <Button variant="outline">
                      <Settings className="w-4 h-4 mr-2" />
                      Configure System
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tips and Best Practices */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                Pro Tips
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong>Balanced Learning:</strong> Start with the Balanced preset for optimal results.
                    You can always adjust later based on your needs.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong>Regular Exports:</strong> Export your knowledge base regularly to create backups
                    of your accumulated wisdom.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong>Monitor Quality:</strong> Watch the exploration/exploitation ratio to ensure
                    the system maintains a healthy balance.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong>Resource Usage:</strong> If performance slows, check the Performance tab
                    and adjust learning parameters accordingly.
                  </span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Dashboard;
