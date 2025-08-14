// HRM Neural Reasoning Dashboard
// Displays HRM metrics, confidence gap, and model status

import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useHRMStore } from '@/stores/useHRMStore';
import { useHRMSocket } from '@/hooks/useHRMSocket';
import { 
  Brain, 
  Cpu, 
  Zap, 
  TrendingUp, 
  Activity,
  Database,
  BarChart3,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { motion } from 'framer-motion';

const HRMDashboard: React.FC = () => {
  const hrm = useHRMStore(state => state.hrm);
  const { requestMetrics, requestTrainingStatus } = useHRMSocket();

  // Auto-refresh metrics
  useEffect(() => {
    requestMetrics();
    requestTrainingStatus();
    
    const interval = setInterval(() => {
      requestMetrics();
    }, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  // Calculate recent performance
  const recentQueries = hrm.queryHistory.slice(0, 20);
  const avgConfidence = recentQueries.length > 0
    ? recentQueries.reduce((sum, q) => sum + q.confidence, 0) / recentQueries.length
    : 0;
  
  const accuracyRate = recentQueries.length > 0
    ? recentQueries.filter(q => 
        (q.isTrue && q.confidence > 0.7) || (!q.isTrue && q.confidence < 0.3)
      ).length / recentQueries.length * 100
    : 0;

  // Status color coding
  const getStatusColor = (status: string) => {
    switch(status) {
      case 'operational': return 'text-green-500';
      case 'training': return 'text-yellow-500';
      case 'offline': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getGapQuality = (gap: number) => {
    if (gap >= 0.8) return { label: 'Excellent', color: 'text-green-500' };
    if (gap >= 0.7) return { label: 'Good', color: 'text-blue-500' };
    if (gap >= 0.5) return { label: 'Fair', color: 'text-yellow-500' };
    return { label: 'Poor', color: 'text-red-500' };
  };

  const gapQuality = getGapQuality(hrm.metrics.confidenceGap);

  return (
    <div className="space-y-4">
      {/* Header Section */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Brain className="w-8 h-8 text-primary" />
          <div>
            <h2 className="text-2xl font-bold">HRM Neural Reasoning System</h2>
            <p className="text-sm text-muted-foreground">
              Hierarchical Reasoning Model - HAK/GAL Compliant
            </p>
          </div>
        </div>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => {
            requestMetrics();
            requestTrainingStatus();
          }}
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Model Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="border-0 bg-card/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Cpu className="w-4 h-4" />
                Model Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className={`text-2xl font-bold capitalize ${getStatusColor(hrm.metrics.modelStatus)}`}>
                  {hrm.metrics.modelStatus}
                </span>
                {hrm.metrics.modelStatus === 'operational' && (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                )}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Device: {hrm.metrics.device}
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Confidence Gap */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-0 bg-card/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Confidence Gap
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">
                  {(hrm.metrics.confidenceGap * 100).toFixed(1)}%
                </span>
                <Badge variant="outline" className={gapQuality.color}>
                  {gapQuality.label}
                </Badge>
              </div>
              <Progress 
                value={hrm.metrics.confidenceGap * 100} 
                className="mt-2 h-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Target: &gt;70%
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Model Parameters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="border-0 bg-card/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Database className="w-4 h-4" />
                Model Size
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                <p className="text-lg font-bold">
                  {(hrm.metrics.parameters / 1000).toFixed(0)}K
                </p>
                <p className="text-xs text-muted-foreground">
                  Parameters
                </p>
                <div className="flex items-center gap-2 text-xs">
                  <span>Vocab: {hrm.metrics.vocabulary}</span>
                  <span>•</span>
                  <span>Facts: {hrm.metrics.factsLoaded}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Performance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="border-0 bg-card/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                <p className="text-lg font-bold">
                  {accuracyRate.toFixed(1)}%
                </p>
                <p className="text-xs text-muted-foreground">
                  Accuracy Rate
                </p>
                <div className="flex items-center gap-2 text-xs">
                  <span>Queries: {hrm.queryHistory.length}</span>
                  <span>•</span>
                  <span>Avg: {(avgConfidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Training Status */}
      {hrm.training && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="border-0 bg-card/50">
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Training Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">Total Epochs</p>
                  <p className="text-lg font-bold">{hrm.training.totalEpochsTrained}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Best Gap</p>
                  <p className="text-lg font-bold">
                    {(hrm.training.bestGapAchieved * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Sessions</p>
                  <p className="text-lg font-bold">{hrm.training.trainingSessions}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Ready</p>
                  <p className="text-lg font-bold">
                    {hrm.training.readyForTraining ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-500" />
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Recent Queries */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card className="border-0 bg-card/50">
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Recent Queries
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {recentQueries.slice(0, 5).map((query, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <span className="font-mono truncate flex-1 mr-2">
                    {query.query}
                  </span>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant="outline" 
                      className={query.confidence > 0.7 ? 'text-green-500' : query.confidence < 0.3 ? 'text-red-500' : 'text-yellow-500'}
                    >
                      {(query.confidence * 100).toFixed(0)}%
                    </Badge>
                    {query.isTrue ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-500" />
                    )}
                  </div>
                </div>
              ))}
              {recentQueries.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No queries yet. Try asking "IsA(Socrates, Philosopher)"
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Prometheus Metrics (if available) */}
      {Object.keys(hrm.prometheus).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card className="border-0 bg-card/50">
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Prometheus Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                {hrm.prometheus.hrm_requests_total && (
                  <div>
                    <p className="text-xs text-muted-foreground">Total Requests</p>
                    <p className="font-bold">{hrm.prometheus.hrm_requests_total}</p>
                  </div>
                )}
                {hrm.prometheus.hrm_request_duration_avg && (
                  <div>
                    <p className="text-xs text-muted-foreground">Avg Duration</p>
                    <p className="font-bold">{hrm.prometheus.hrm_request_duration_avg.toFixed(1)}ms</p>
                  </div>
                )}
                {hrm.prometheus.hrm_batch_size_avg && (
                  <div>
                    <p className="text-xs text-muted-foreground">Avg Batch Size</p>
                    <p className="font-bold">{hrm.prometheus.hrm_batch_size_avg.toFixed(0)}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
};

export default HRMDashboard;
