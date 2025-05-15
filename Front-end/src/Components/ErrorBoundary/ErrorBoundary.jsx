import React from 'react';
import styles from './ErrorBoundary.module.css';
import { Link } from 'react-router-dom';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Rendering error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className={styles.errorContainer}>
          <h1>Something went wrong</h1>
          <p>We're sorry, but there was an error loading this page</p>
          <Link to="/" className={styles.homeButton}>Back to Home</Link>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;