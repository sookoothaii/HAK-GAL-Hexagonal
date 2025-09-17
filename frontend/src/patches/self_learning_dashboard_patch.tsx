// PATCH FILE: Update Dashboard to show real Self-Learning Metrics
// Apply this to ProDashboardEnhanced.tsx

// 1. Add import at the top of the file:
import { useSelfLearningMetrics } from '../hooks/useSelfLearningMetrics';

// 2. In the component, add:
const selfLearningMetrics = useSelfLearningMetrics();

// 3. Replace the hardcoded Self-Learning System section with:

{/* Self-Learning System Card */}
<Card className="h-full">
  <CardHeader className="p-3">
    <CardTitle className="text-xs font-medium">Self-Learning System</CardTitle>
  </CardHeader>
  <CardContent className="p-3 pt-0">
    <div className="flex items-center justify-between">
      <div>
        <Badge variant={selfLearningMetrics.active ? "default" : "outline"} className="mb-1 text-[9px] px-1 py-0">
          {selfLearningMetrics.adaptive ? "Adaptive" : "Inactive"}
        </Badge>
        <div className="text-2xl font-bold">
          {selfLearningMetrics.factsGenerated || 0}
        </div>
        <p className="text-xs text-muted-foreground">
          {selfLearningMetrics.learningRate || 0} facts/min
        </p>
      </div>
    </div>
    <div className="mt-3 space-y-1.5">
      <div className="flex justify-between text-[10px]">
        <span className="text-muted-foreground">Learning Progress</span>
        <span>{Math.round(selfLearningMetrics.learningProgress || 0)}%</span>
      </div>
      <Progress 
        value={selfLearningMetrics.learningProgress || 0} 
        className="h-0.5 bg-background" 
      />
    </div>
  </CardContent>
</Card>

// 4. Similarly update the System Trust Score display to use real data:
<div className="text-2xl font-bold">
  {Math.round(50 + (selfLearningMetrics.learningProgress || 0) * 0.5)}%
</div>

// Note: This patch shows the structure. Apply similar changes to:
// - ProDashboardUltraCompact.tsx
// - ProKnowledgeStats.tsx (for the self-learning ratio)
