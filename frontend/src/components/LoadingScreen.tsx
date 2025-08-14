import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Brain, Network, Cpu, Database, Zap } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

const LoadingScreen: React.FC = () => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  
  const loadingSteps = [
    { icon: <Database className="w-6 h-6" />, label: 'Initializing Knowledge Base', duration: 300 },
    { icon: <Network className="w-6 h-6" />, label: 'Establishing WebSocket Connection', duration: 400 },
    { icon: <Brain className="w-6 h-6" />, label: 'Loading Neural Networks', duration: 500 },
    { icon: <Cpu className="w-6 h-6" />, label: 'Starting Engines', duration: 300 },
    { icon: <Zap className="w-6 h-6" />, label: 'Activating Governor', duration: 200 },
  ];
  
  useEffect(() => {
    const totalDuration = loadingSteps.reduce((acc, step) => acc + step.duration, 0);
    let elapsed = 0;
    let stepIndex = 0;
    let stepElapsed = 0;
    
    const interval = setInterval(() => {
      elapsed += 20;
      stepElapsed += 20;
      
      // Update progress
      const progressPercent = (elapsed / totalDuration) * 100;
      setProgress(Math.min(progressPercent, 100));
      
      // Check if we should move to next step
      if (stepIndex < loadingSteps.length && stepElapsed >= loadingSteps[stepIndex].duration) {
        stepElapsed = 0;
        stepIndex++;
        if (stepIndex < loadingSteps.length) {
          setCurrentStep(stepIndex);
        }
      }
      
      // Stop when complete
      if (elapsed >= totalDuration) {
        clearInterval(interval);
      }
    }, 20);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="fixed inset-0 bg-background flex items-center justify-center overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-background to-secondary/20" />
        <div className="absolute inset-0">
          {[...Array(50)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-primary/30 rounded-full"
              initial={{
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
              }}
              animate={{
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
              }}
              transition={{
                duration: Math.random() * 20 + 10,
                repeat: Infinity,
                repeatType: 'reverse',
                ease: 'linear',
              }}
            />
          ))}
        </div>
      </div>
      
      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center space-y-8 p-8">
        {/* Logo Animation */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 0.8, type: 'spring' }}
          className="relative"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-0"
          >
            <Sparkles className="w-24 h-24 text-primary opacity-20" />
          </motion.div>
          <Brain className="w-24 h-24 text-primary relative" />
        </motion.div>
        
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent">
            HAK-GAL Suite
          </h1>
          <p className="text-muted-foreground mt-2">
            Neuro-Symbolic AI Platform
          </p>
        </motion.div>
        
        {/* Loading Steps */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="w-80"
        >
          <div className="space-y-4">
            {loadingSteps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ 
                  opacity: index <= currentStep ? 1 : 0.3,
                  x: 0
                }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center gap-3"
              >
                <motion.div
                  animate={{
                    scale: index === currentStep ? [1, 1.2, 1] : 1,
                  }}
                  transition={{
                    duration: 0.5,
                    repeat: index === currentStep ? Infinity : 0,
                    repeatType: 'reverse',
                  }}
                  className={`p-2 rounded-lg ${
                    index < currentStep 
                      ? 'bg-primary/20 text-primary' 
                      : index === currentStep
                      ? 'bg-primary/30 text-primary'
                      : 'bg-muted/20 text-muted-foreground'
                  }`}
                >
                  {step.icon}
                </motion.div>
                <span className={`text-sm ${
                  index <= currentStep ? 'text-foreground' : 'text-muted-foreground'
                }`}>
                  {step.label}
                </span>
                {index < currentStep && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="ml-auto"
                  >
                    <div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
                      <motion.div
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: 1 }}
                        transition={{ duration: 0.3 }}
                      >
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      </motion.div>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </div>
          
          {/* Progress Bar */}
          <div className="mt-8 space-y-2">
            <Progress value={progress} className="h-2" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Loading system components...</span>
              <span>{Math.round(progress)}%</span>
            </div>
          </div>
        </motion.div>
        
        {/* Fun Facts */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="text-center max-w-md"
        >
          <p className="text-xs text-muted-foreground">
            Did you know? The HAK-GAL system can process over 10,000 knowledge queries per second
            with 99.9% accuracy using its hybrid neuro-symbolic architecture.
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default LoadingScreen;
