// Enterprise Error Handling and Monitoring System
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Bug, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';

interface ErrorDetails {
  message: string;
  stack?: string;
  componentStack?: string;
  timestamp: number;
  userAgent: string;
  url: string;
  sessionId: string;
  errorBoundary?: string;
  additionalContext?: Record<string, any>;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorCount: number;
  lastErrorTime: number;
  isReporting: boolean;
  userFeedback: string;
}

// Error telemetry service
class ErrorTelemetryService {
  private static instance: ErrorTelemetryService;
  private errorQueue: ErrorDetails[] = [];
  private isOnline = navigator.onLine;

  static getInstance(): ErrorTelemetryService {
    if (!ErrorTelemetryService.instance) {
      ErrorTelemetryService.instance = new ErrorTelemetryService();
    }
    return ErrorTelemetryService.instance;
  }

  constructor() {
    // Monitor online status
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.flushErrorQueue();
    });
    
    window.addEventListener('offline', () => {
      this.isOnline = false;
    });

    // Global error handler
    window.addEventListener('error', (event) => {
      this.captureError(event.error, {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    });

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.captureError(new Error(event.reason), {
        type: 'unhandledRejection',
        promise: event.promise,
      });
    });
  }

  captureError(error: Error, context?: Record<string, any>): void {
    const errorDetails: ErrorDetails = {
      message: error.message,
      stack: error.stack,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: this.getSessionId(),
      additionalContext: context,
    };

    // Store locally
    this.errorQueue.push(errorDetails);
    this.saveToLocalStorage();

    // Attempt to send immediately if online
    if (this.isOnline) {
      this.sendError(errorDetails);
    }
  }

  private getSessionId(): string {
    let sessionId = sessionStorage.getItem('hak-gal-session-id');
    if (!sessionId) {
      sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('hak-gal-session-id', sessionId);
    }
    return sessionId;
  }

  private saveToLocalStorage(): void {
    try {
      localStorage.setItem('hak-gal-error-queue', JSON.stringify(this.errorQueue.slice(-50)));
    } catch (e) {
      console.error('Failed to save errors to localStorage:', e);
    }
  }

  private loadFromLocalStorage(): void {
    try {
      const stored = localStorage.getItem('hak-gal-error-queue');
      if (stored) {
        this.errorQueue = JSON.parse(stored);
      }
    } catch (e) {
      console.error('Failed to load errors from localStorage:', e);
    }
  }

  private async sendError(error: ErrorDetails): Promise<void> {
    try {
      // In production, this would send to your error tracking service
      console.error('Error captured:', error);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Remove from queue if successful
      this.errorQueue = this.errorQueue.filter(e => e.timestamp !== error.timestamp);
      this.saveToLocalStorage();
    } catch (e) {
      console.error('Failed to send error:', e);
    }
  }

  private async flushErrorQueue(): Promise<void> {
    const errors = [...this.errorQueue];
    for (const error of errors) {
      await this.sendError(error);
    }
  }

  async reportErrorWithFeedback(error: Error, errorInfo: ErrorInfo, feedback: string): Promise<void> {
    const errorDetails: ErrorDetails = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: this.getSessionId(),
      additionalContext: {
        userFeedback: feedback,
      },
    };

    await this.sendError(errorDetails);
  }
}

// Enhanced Error Boundary Component
export class EnterpriseErrorBoundary extends Component<
  { children: ReactNode; fallback?: ReactNode; name?: string },
  ErrorBoundaryState
> {
  private telemetry = ErrorTelemetryService.getInstance();
  private retryTimeouts: NodeJS.Timeout[] = [];

  constructor(props: { children: ReactNode; fallback?: ReactNode; name?: string }) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
      lastErrorTime: 0,
      isReporting: false,
      userFeedback: '',
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      lastErrorTime: Date.now(),
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to telemetry
    this.telemetry.captureError(error, {
      errorBoundary: this.props.name || 'Unknown',
      componentStack: errorInfo.componentStack,
    });

    // Update state with error details
    this.setState(prevState => ({
      errorInfo,
      errorCount: prevState.errorCount + 1,
    }));

    // Implement exponential backoff for auto-retry
    if (this.state.errorCount < 3) {
      const retryDelay = Math.pow(2, this.state.errorCount) * 1000;
      const timeout = setTimeout(() => {
        this.setState({ hasError: false, error: null, errorInfo: null });
      }, retryDelay);
      this.retryTimeouts.push(timeout);
    }
  }

  componentWillUnmount() {
    // Clean up retry timeouts
    this.retryTimeouts.forEach(timeout => clearTimeout(timeout));
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
      userFeedback: '',
    });
  };

  handleReport = async () => {
    if (!this.state.error || !this.state.errorInfo) return;

    this.setState({ isReporting: true });

    try {
      await this.telemetry.reportErrorWithFeedback(
        this.state.error,
        this.state.errorInfo,
        this.state.userFeedback
      );
      
      toast.success('Error report sent successfully. Thank you for your feedback!');
      this.handleReset();
    } catch (e) {
      toast.error('Failed to send error report. Please try again.');
    } finally {
      this.setState({ isReporting: false });
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return <>{this.props.fallback}</>;
      }

      // Default error UI
      return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background to-background/95">
          <Card className="w-full max-w-2xl border-0 shadow-2xl">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-destructive/10 rounded-full">
                  <AlertTriangle className="w-6 h-6 text-destructive" />
                </div>
                <div>
                  <CardTitle className="text-2xl">Oops! Something went wrong</CardTitle>
                  <CardDescription>
                    An unexpected error occurred in the {this.props.name || 'application'}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <Alert>
                <Bug className="h-4 w-4" />
                <AlertTitle>Error Details</AlertTitle>
                <AlertDescription className="mt-2 font-mono text-sm">
                  {this.state.error?.message || 'Unknown error'}
                </AlertDescription>
              </Alert>

              {this.state.errorCount > 1 && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>Multiple Errors Detected</AlertTitle>
                  <AlertDescription>
                    This error has occurred {this.state.errorCount} times. The component may be unstable.
                  </AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Help us improve by describing what you were doing:
                </label>
                <Textarea
                  placeholder="I was trying to..."
                  value={this.state.userFeedback}
                  onChange={(e) => this.setState({ userFeedback: e.target.value })}
                  className="min-h-[100px]"
                />
              </div>

              {/* Expandable technical details */}
              <details className="cursor-pointer">
                <summary className="text-sm font-medium text-muted-foreground hover:text-foreground">
                  Show technical details
                </summary>
                <div className="mt-2 p-4 bg-muted/50 rounded-lg">
                  <pre className="text-xs overflow-auto max-h-48">
                    {this.state.error?.stack}
                  </pre>
                  {this.state.errorInfo?.componentStack && (
                    <pre className="text-xs overflow-auto max-h-48 mt-2">
                      Component Stack:
                      {this.state.errorInfo.componentStack}
                    </pre>
                  )}
                </div>
              </details>
            </CardContent>

            <CardFooter className="flex gap-2">
              <Button
                onClick={this.handleReset}
                className="flex-1"
                variant="default"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>
              <Button
                onClick={this.handleReport}
                className="flex-1"
                variant="outline"
                disabled={this.state.isReporting}
              >
                <Send className="w-4 h-4 mr-2" />
                {this.state.isReporting ? 'Sending...' : 'Send Report'}
              </Button>
            </CardFooter>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Async Error Boundary for Suspense
export const AsyncErrorBoundary: React.FC<{ children: ReactNode; name?: string }> = ({ children, name }) => {
  return (
    <EnterpriseErrorBoundary name={name}>
      <React.Suspense fallback={<LoadingFallback />}>
        {children}
      </React.Suspense>
    </EnterpriseErrorBoundary>
  );
};

// Loading fallback component
const LoadingFallback: React.FC = () => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="w-12 h-12 border-4 border-primary/20 rounded-full animate-pulse" />
          <div className="absolute inset-0 w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
};

// HOC for easy error boundary wrapping
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryName?: string
): React.FC<P> {
  return (props: P) => (
    <EnterpriseErrorBoundary name={errorBoundaryName}>
      <Component {...props} />
    </EnterpriseErrorBoundary>
  );
}
