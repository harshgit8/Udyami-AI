import { format, formatDistanceToNow, isValid } from 'date-fns';

export const formatDate = (date: Date | string | number): string => {
  const dateObj = new Date(date);
  if (!isValid(dateObj)) return 'Invalid date';
  return format(dateObj, 'MMM dd, yyyy');
};

export const formatDateTime = (date: Date | string | number): string => {
  const dateObj = new Date(date);
  if (!isValid(dateObj)) return 'Invalid date';
  return format(dateObj, 'MMM dd, yyyy HH:mm');
};

export const formatTime = (date: Date | string | number): string => {
  const dateObj = new Date(date);
  if (!isValid(dateObj)) return 'Invalid time';
  return format(dateObj, 'HH:mm:ss');
};

export const formatRelativeTime = (date: Date | string | number): string => {
  const dateObj = new Date(date);
  if (!isValid(dateObj)) return 'Invalid date';
  return formatDistanceToNow(dateObj, { addSuffix: true });
};

export const formatNumber = (num: number, decimals: number = 0): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
};

export const formatCurrency = (amount: number, currency: string = 'INR'): string => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
  }).format(amount);
};

export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${formatNumber(value, decimals)}%`;
};

export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
};

export const formatFileSize = (bytes: number): string => {
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 Bytes';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`;
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const formatOrderId = (orderId: string): string => {
  return orderId.toUpperCase();
};

export const formatMachineId = (machineId: string): string => {
  return machineId.toUpperCase();
};

export const formatProductType = (productType: string): string => {
  return productType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export const formatPriority = (priority: string): string => {
  const priorityMap: Record<string, string> = {
    low: 'Low',
    normal: 'Normal',
    high: 'High',
    critical: 'Critical',
  };
  return priorityMap[priority.toLowerCase()] || priority;
};

export const formatStatus = (status: string): string => {
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};