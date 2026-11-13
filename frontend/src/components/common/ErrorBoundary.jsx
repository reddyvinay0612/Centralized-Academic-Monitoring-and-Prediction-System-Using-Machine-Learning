import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[CAMPS-ML ErrorBoundary] Captured render error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[450px] flex-col items-center justify-center p-6 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-risk-high/10 text-risk-high shadow-sm mb-4">
            <AlertTriangle className="h-8 w-8" />
          </div>
          <h2 className="font-heading text-xl font-bold text-ink dark:text-dark-text">
            Dashboard View Encountered an Issue
          </h2>
          <p className="mt-2 max-w-md text-caption text-muted dark:text-dark-muted">
            The page could not render completely. This may be due to an active data synchronization or an interrupted network request.
          </p>
          <div className="mt-6 flex items-center gap-3">
            <Button variant="primary" size="md" onClick={this.handleReload} className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" />
              Reload Dashboard
            </Button>
            <Button variant="outline" size="md" onClick={this.handleGoHome} className="flex items-center gap-2">
              <Home className="h-4 w-4" />
              Return Home
            </Button>
          </div>
          {process.env.NODE_ENV !== 'production' && this.state.error && (
            <details className="mt-6 max-w-lg text-left text-xs text-muted dark:text-dark-muted bg-surface dark:bg-dark-surface p-3 rounded-card border border-line dark:border-dark-line">
              <summary className="cursor-pointer font-mono font-bold text-risk-high">
                {this.state.error.toString()}
              </summary>
              <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-[10px]">
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
