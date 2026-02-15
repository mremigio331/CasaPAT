import { useTheme, useMediaQuery } from '@mui/material';
import { useState, useEffect } from 'react';

/**
 * Custom hook to detect screen size for responsive layouts
 * Uses Material-UI breakpoints to determine device type
 * 
 * @returns {Object} Object containing responsive flags and screen width
 * @returns {boolean} isMobile - True if screen width < 600px
 * @returns {boolean} isTablet - True if screen width between 600px and 960px
 * @returns {boolean} isDesktop - True if screen width > 960px
 * @returns {number} screenWidth - Current window width in pixels
 */
const useResponsive = () => {
  const theme = useTheme();
  
  // Define breakpoints
  const isMobile = useMediaQuery(theme.breakpoints.down('sm')); // < 600px
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md')); // 600px - 960px
  const isDesktop = useMediaQuery(theme.breakpoints.up('md')); // > 960px
  
  // Track actual screen width
  const [screenWidth, setScreenWidth] = useState(
    typeof window !== 'undefined' ? window.innerWidth : 0
  );

  useEffect(() => {
    // Handle window resize
    const handleResize = () => {
      setScreenWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return {
    isMobile,
    isTablet,
    isDesktop,
    screenWidth,
  };
};

export default useResponsive;
