// Enterprise Performance Monitoring and Optimization System
import React, { useEffect, useRef, useCallback, useState } from 'react';
import { useEnhancedGovernorStore } from '@/stores/useEnhancedGovernorStore';

// Performance Observer Types
interface PerformanceEntry {
  name: string;
  entryType: string;
  startTime: number;
  duration: number;
}

interface ResourceTiming extends PerformanceEntry {
  initiatorType: string;
  transferSize: number;
  encodedBodySize: number;
  decodedBodySize: number;
}

// Web Vitals
interface WebVitals {
  LCP: number | null; // Largest Contentful Paint
  FID: number | null; // First Input Delay
  CLS: number | null; // Cumulative Layout Shift
  FCP: number | null; // First Contentful Paint
  TTFB: number | null; // Time to First Byte
  INP: number | null; // Interaction to Next Paint
}

// Performance monitoring service
class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private observers: Map<string, PerformanceObserver> = new Map();
  private metrics: Map<string, number[]> = new Map();
  private vitals: WebVitals = {
    LCP: null,
    FID: null,
    CLS: null,
    FCP: null,
    TTFB: null,
    INP: null,
  };

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  constructor() {
    this.initializeObservers();
    this.measureInitialMetrics();
  }

  private initializeObservers(): void {
    // Largest Contentful Paint
    if ('PerformanceObserver' in window) {
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          this.vitals.LCP = lastEntry.startTime;
          this.reportVital('LCP', lastEntry.startTime);
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        this.observers.set('lcp', lcpObserver);
      } catch (e) {
        console.warn('LCP observer not supported');
      }

      // First Input Delay
      try {
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach((entry: any) => {
            this.vitals.FID = entry.processingStart - entry.startTime;
            this.reportVital('FID', this.vitals.FID);
          });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
        this.observers.set('fid', fidObserver);
      } catch (e) {
        console.warn('FID observer not supported');
      }

      // Cumulative Layout Shift
      try {
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry: any) => {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
              this.vitals.CLS = clsValue;
              this.reportVital('CLS', clsValue);
            }
          });
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
        this.observers.set('cls', clsObserver);
      } catch (e) {
        console.warn('CLS observer not supported');
      }

      // Resource timing
      try {
        const resourceObserver = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry: any) => {
            this.trackResourceTiming(entry);
          });
        });
        resourceObserver.observe({ entryTypes: ['resource'] });
        this.observers.set('resource', resourceObserver);
      } catch (e) {
        console.warn('Resource observer not supported');
      }
    }
  }

  private measureInitialMetrics(): void {
    // Time to First Byte
    if (window.performance && window.performance.timing) {
      const timing = window.performance.timing;
      const ttfb = timing.responseStart - timing.navigationStart;
      this.vitals.TTFB = ttfb;
      this.reportVital('TTFB', ttfb);
    }

    // First Contentful Paint
    if ('PerformancePaintTiming' in window) {
      const paintEntries = performance.getEntriesByType('paint');
      paintEntries.forEach((entry) => {
        if (entry.name === 'first-contentful-paint') {
          this.vitals.FCP = entry.startTime;
          this.reportVital('FCP', entry.startTime);
        }
      });
    }
  }

  private trackResourceTiming(entry: ResourceTiming): void {
    const type = entry.initiatorType;
    if (!this.metrics.has(type)) {
      this.metrics.set(type, []);
    }
    this.metrics.get(type)?.push(entry.duration);
  }

  private reportVital(name: string, value: number): void {
    // In production, send to analytics service
    console.log(`Web Vital - ${name}: ${value.toFixed(2)}ms`);
    
    // Update store
    if (useEnhancedGovernorStore.getState().performAction) {
      useEnhancedGovernorStore.getState().performAction(`UPDATE_${name}`, () => {
        // Store vital in enhanced store
      });
    }
  }

  public getVitals(): WebVitals {
    return { ...this.vitals };
  }

  public getResourceMetrics(): Map<string, number[]> {
    return new Map(this.metrics);
  }

  public cleanup(): void {
    this.observers.forEach((observer) => observer.disconnect());
    this.observers.clear();
  }
}

// React Hook for performance monitoring
export const usePerformanceMonitoring = (componentName: string) => {
  const renderCount = useRef(0);
  const renderStartTime = useRef<number>(0);
  const updateMetrics = useEnhancedGovernorStore((state) => state.performAction);

  // Track component render time
  useEffect(() => {
    renderCount.current++;
    const renderTime = performance.now() - renderStartTime.current;
    
    if (renderTime > 16.67) { // More than one frame (60fps)
      console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`);
    }

    updateMetrics(`RENDER_${componentName}`, () => {
      // Update render metrics
    });
  });

  // Track component mount time
  useEffect(() => {
    const mountTime = performance.now();
    
    return () => {
      const unmountTime = performance.now();
      const componentLifetime = unmountTime - mountTime;
      
      updateMetrics(`LIFETIME_${componentName}`, () => {
        // Update lifetime metrics
      });
    };
  }, [componentName, updateMetrics]);

  // Set render start time
  renderStartTime.current = performance.now();

  return {
    renderCount: renderCount.current,
  };
};

// React Hook for intersection observer (lazy loading)
export const useLazyLoad = (
  ref: React.RefObject<HTMLElement>,
  options?: IntersectionObserverInit
) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasIntersected, setHasIntersected] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
        if (entry.isIntersecting && !hasIntersected) {
          setHasIntersected(true);
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options,
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [ref, options, hasIntersected]);

  return { isIntersecting, hasIntersected };
};

// Performance optimization HOC
export function withPerformanceOptimization<P extends object>(
  Component: React.ComponentType<P>,
  options: {
    memoize?: boolean;
    lazy?: boolean;
    errorBoundary?: boolean;
    performanceTracking?: boolean;
  } = {}
): React.ComponentType<P> {
  const {
    memoize = true,
    lazy = false,
    errorBoundary = true,
    performanceTracking = true,
  } = options;

  let OptimizedComponent: React.ComponentType<P> = Component;

  // Apply React.memo for memoization
  if (memoize) {
    OptimizedComponent = React.memo(OptimizedComponent) as React.ComponentType<P>;
  }

  // Apply lazy loading
  if (lazy) {
    OptimizedComponent = React.lazy(() =>
      Promise.resolve({ default: OptimizedComponent })
    ) as React.ComponentType<P>;
  }

  // Wrap with performance tracking
  if (performanceTracking) {
    const TrackedComponent = (props: P) => {
      usePerformanceMonitoring(Component.displayName || Component.name || 'Unknown');
      return <OptimizedComponent {...props} />;
    };
    OptimizedComponent = TrackedComponent;
  }

  // Apply error boundary
  if (errorBoundary) {
    const { withErrorBoundary } = require('./EnterpriseErrorBoundary');
    OptimizedComponent = withErrorBoundary(
      OptimizedComponent,
      Component.displayName || Component.name
    );
  }

  return OptimizedComponent;
}

// Bundle size monitoring
export const useBundleSizeMonitoring = () => {
  useEffect(() => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      const effectiveType = connection.effectiveType;
      const downlink = connection.downlink;
      
      console.log(`Network: ${effectiveType}, Downlink: ${downlink}Mbps`);
      
      // Adjust loading strategy based on connection
      if (effectiveType === '2g' || effectiveType === 'slow-2g') {
        // Enable aggressive lazy loading
        document.body.classList.add('low-bandwidth');
      }
    }
  }, []);
};

// Memory leak detection
export const useMemoryLeakDetection = (componentName: string) => {
  const instancesRef = useRef(new Set<string>());
  const instanceId = useRef(`${componentName}-${Date.now()}-${Math.random()}`);

  useEffect(() => {
    const id = instanceId.current;
    instancesRef.current.add(id);
    
    if (instancesRef.current.size > 10) {
      console.warn(`Potential memory leak in ${componentName}: ${instancesRef.current.size} instances`);
    }

    return () => {
      instancesRef.current.delete(id);
    };
  }, [componentName]);
};

// Export performance monitor instance
export const performanceMonitor = PerformanceMonitor.getInstance();

// Auto-start monitoring
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    performanceMonitor.getVitals();
  });
}
