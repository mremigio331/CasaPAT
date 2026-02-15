import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ErrorBoundary from './components/ErrorBoundary';
import NavBar from './components/NavBar';
import HomePage from './pages/HomePage';
import AirQualityHistoryPage from './pages/AirQualityHistoryPage';
import DoorHistoryPage from './pages/DoorHistoryPage';
import theme from './theme';

// Create QueryClient with retry and refetch configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 2, // 2 minutes - data is considered fresh for 2 minutes
      cacheTime: 1000 * 60 * 10, // 10 minutes - unused data stays in cache for 10 minutes
      refetchInterval: 1000 * 60 * 5, // 5 minutes - automatic refetch every 5 minutes
      refetchOnWindowFocus: true, // Refetch when window regains focus
      retry: 3, // Retry failed requests 3 times
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <NavBar title="CasaPAT IoT Dashboard" />
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/air-quality-history" element={<AirQualityHistoryPage />} />
              <Route path="/door-history" element={<DoorHistoryPage />} />
            </Routes>
          </BrowserRouter>
        </QueryClientProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
