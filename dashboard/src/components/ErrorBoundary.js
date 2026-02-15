import React, { Component } from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

/**
 * ErrorBoundary component catches React errors in child components
 * and displays a fallback UI with error details and a reload option.
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details to console
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Update state with error details
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReload = () => {
    // Reload the page
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Render custom fallback UI if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          minHeight="100vh"
          p={3}
        >
          <Paper
            elevation={3}
            sx={{
              p: 4,
              maxWidth: 600,
              textAlign: 'center',
            }}
          >
            <ErrorOutlineIcon
              color="error"
              sx={{ fontSize: 64, mb: 2 }}
            />
            <Typography variant="h5" gutterBottom>
              Something went wrong
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              An unexpected error occurred. Please try reloading the page.
            </Typography>
            {this.state.error && (
              <Typography
                variant="body2"
                color="error"
                sx={{
                  mt: 2,
                  p: 2,
                  bgcolor: 'error.light',
                  borderRadius: 1,
                  fontFamily: 'monospace',
                  textAlign: 'left',
                  overflow: 'auto',
                }}
              >
                {this.state.error.toString()}
              </Typography>
            )}
            <Button
              variant="contained"
              color="primary"
              onClick={this.handleReload}
              sx={{ mt: 3 }}
            >
              Reload Page
            </Button>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
