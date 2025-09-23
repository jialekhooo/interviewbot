import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, info: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // You could log this to a monitoring service
    // eslint-disable-next-line no-console
    console.error("App crashed:", error, info);
    this.setState({ info });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="container mx-auto px-4 py-10">
          <div className="max-w-2xl mx-auto bg-white shadow rounded p-6">
            <h1 className="text-2xl font-bold text-red-600 mb-2">Something went wrong</h1>
            <p className="text-sm text-gray-700 mb-4">The app encountered a runtime error. Details below can help debug.</p>
            <pre className="text-xs overflow-auto bg-gray-50 p-3 rounded mb-3">
{String(this.state.error)}
{this.state.info ? "\n\n" + this.state.info.componentStack : ""}
            </pre>
            <button className="px-3 py-2 bg-blue-600 text-white rounded" onClick={() => window.location.reload()}>Reload</button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
