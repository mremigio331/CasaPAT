import { formatDistanceToNow, format } from 'date-fns';

/**
 * Format a date as relative time (e.g., "2 minutes ago", "1 hour ago")
 * @param {Date|string|number} date - The date to format
 * @returns {string} Formatted relative time string
 */
export function formatRelativeTime(date) {
  if (!date) {
    return 'Unknown';
  }

  try {
    const dateObj = date instanceof Date ? date : new Date(date);
    
    if (isNaN(dateObj.getTime())) {
      return 'Invalid date';
    }

    return formatDistanceToNow(dateObj, { addSuffix: true });
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return 'Invalid date';
  }
}

/**
 * Check if a timestamp is stale (older than a threshold)
 * @param {Date|string|number} date - The date to check
 * @param {number} threshold - Threshold in milliseconds (default: 10 minutes)
 * @returns {boolean} True if the timestamp is stale
 */
export function isStaleTimestamp(date, threshold = 10 * 60 * 1000) {
  if (!date) {
    return true;
  }

  try {
    const dateObj = date instanceof Date ? date : new Date(date);
    
    if (isNaN(dateObj.getTime())) {
      return true;
    }

    const now = new Date();
    const diff = now.getTime() - dateObj.getTime();
    
    return diff > threshold;
  } catch (error) {
    console.error('Error checking timestamp staleness:', error);
    return true;
  }
}

/**
 * Format a timestamp for chart x-axis display
 * @param {Date|string|number} date - The date to format
 * @returns {string} Formatted timestamp for charts (e.g., "12:30 PM" or "Jan 15")
 */
export function formatChartTimestamp(date) {
  if (!date) {
    return '';
  }

  try {
    const dateObj = date instanceof Date ? date : new Date(date);
    
    if (isNaN(dateObj.getTime())) {
      return 'Invalid';
    }

    const now = new Date();
    const diffInHours = (now.getTime() - dateObj.getTime()) / (1000 * 60 * 60);

    // If within last 24 hours, show time only
    if (diffInHours < 24) {
      return format(dateObj, 'h:mm a');
    }
    
    // If within last 7 days, show day and time
    if (diffInHours < 24 * 7) {
      return format(dateObj, 'MMM d, h:mm a');
    }
    
    // Otherwise show date only
    return format(dateObj, 'MMM d');
  } catch (error) {
    console.error('Error formatting chart timestamp:', error);
    return 'Invalid';
  }
}

/**
 * Convert a date to the user's local timezone
 * @param {Date|string|number} date - The date to convert
 * @returns {Date} Date object in local timezone
 */
export function convertToLocalTimezone(date) {
  if (!date) {
    return null;
  }

  try {
    const dateObj = date instanceof Date ? date : new Date(date);
    
    if (isNaN(dateObj.getTime())) {
      return null;
    }

    // JavaScript Date objects are already in local timezone
    // This function ensures consistent handling and validation
    return dateObj;
  } catch (error) {
    console.error('Error converting to local timezone:', error);
    return null;
  }
}
