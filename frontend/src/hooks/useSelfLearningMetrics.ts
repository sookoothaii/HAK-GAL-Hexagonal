// Self-Learning Metrics Display Component
import React, { useEffect, useState } from 'react';

interface SelfLearningMetrics {
  active: boolean;
  factsGenerated: number;
  learningRate: number;
  learningProgress: number;
  adaptive: boolean;
}

export const useSelfLearningMetrics = () => {
  const [metrics, setMetrics] = useState<SelfLearningMetrics>({
    active: false,
    factsGenerated: 0,
    learningRate: 0,
    learningProgress: 0,
    adaptive: false
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('http://localhost:5002/api/governor/status');
        const data = await response.json();
        
        // Extract metrics from generator data
        if (data.generator) {
          const gen = data.generator;
          const factsGenerated = gen.facts_generated || 0;
          const learningProgress = Math.min(100, (factsGenerated / 10000) * 100);
          
          setMetrics({
            active: gen.active || false,
            factsGenerated: factsGenerated,
            learningRate: Math.round(gen.facts_per_minute || 0),
            learningProgress: learningProgress,
            adaptive: gen.active || false
          });
        } else if (data.self_learning) {
          // Use self_learning if available
          const sl = data.self_learning;
          setMetrics({
            active: sl.active || false,
            factsGenerated: sl.facts_generated || 0,
            learningRate: Math.round(sl.learning_rate || 0),
            learningProgress: sl.learning_progress || 0,
            adaptive: sl.adaptive || false
          });
        }
      } catch (error) {
        console.error('Failed to fetch self-learning metrics:', error);
      }
    };

    // Initial fetch
    fetchMetrics();

    // Set up polling every 5 seconds
    const interval = setInterval(fetchMetrics, 5000);

    return () => clearInterval(interval);
  }, []);

  return metrics;
};

// Export for use in dashboard components
export default useSelfLearningMetrics;
