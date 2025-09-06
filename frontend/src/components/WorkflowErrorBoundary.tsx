import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw, Bug } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class WorkflowErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Workflow Error Boundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Card className="p-6 border-red-200 bg-red-50">
          <div className="flex items-center gap-3 mb-4">
            <Bug className="h-6 w-6 text-red-600" />
            <h2 className="text-lg font-semibold text-red-800">
              Workflow Error
            </h2>
          </div>
          
          <div className="mb-4">
            <p className="text-red-700 mb-2">
              Something went wrong in the workflow system. This could be due to:
            </p>
            <ul className="text-sm text-red-600 list-disc list-inside space-y-1">
              <li>Invalid workflow data</li>
              <li>Missing dependencies</li>
              <li>Network connectivity issues</li>
              <li>Browser compatibility problems</li>
            </ul>
          </div>

          {this.state.error && (
            <details className="mb-4">
              <summary className="cursor-pointer text-sm font-medium text-red-700 mb-2">
                Error Details
              </summary>
              <div className="text-xs font-mono bg-red-100 p-3 rounded border border-red-200 text-red-800">
                <div className="mb-2">
                  <strong>Error:</strong> {this.state.error.message}
                </div>
                {this.state.errorInfo && (
                  <div>
                    <strong>Stack:</strong>
                    <pre className="mt-1 overflow-auto">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </div>
                )}
              </div>
            </details>
          )}

          <div className="flex gap-2">
            <Button
              onClick={this.handleReset}
              variant="outline"
              size="sm"
              className="border-red-300 text-red-700 hover:bg-red-100"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              Try Again
            </Button>
            
            <Button
              onClick={() => window.location.reload()}
              variant="outline"
              size="sm"
              className="border-red-300 text-red-700 hover:bg-red-100"
            >
              Reload Page
            </Button>
          </div>

          <div className="mt-4 p-3 bg-red-100 border border-red-200 rounded">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <span className="text-sm font-medium text-red-700">Need Help?</span>
            </div>
            <p className="text-xs text-red-600">
              If this error persists, try refreshing the page or contact support. 
              The error has been logged for debugging purposes.
            </p>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}


