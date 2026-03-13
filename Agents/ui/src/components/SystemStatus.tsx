import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/solid';
import { useOrchestrator } from '../context/OrchestratorContext';
import { formatDistanceToNow } from 'date-fns';

const SystemStatus: React.FC = () => {
  const { systemStatus } = useOrchestrator();

  const getConnectionStatus = () => {
    if (systemStatus.sheetsConnected && systemStatus.geminiApiStatus === 'connected') {
      return {
        icon: CheckCircleIcon,
        text: 'All systems operational',
        isOperational: true,
      };
    } else if (systemStatus.sheetsConnected || systemStatus.geminiApiStatus === 'connected') {
      return {
        icon: ExclamationTriangleIcon,
        text: 'Partial connectivity',
        isOperational: false,
      };
    } else {
      return {
        icon: XCircleIcon,
        text: 'Connection issues',
        isOperational: false,
      };
    }
  };

  const status = getConnectionStatus();
  const StatusIcon = status.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.05 }}
      className="bg-pure-white border border-mono-200 rounded-lg px-8 py-5 shadow-sm"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-6">
          {/* Status Indicator */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="status-dot"></div>
              {status.isOperational && <div className="status-dot pulse"></div>}
            </div>
            <StatusIcon className="w-5 h-5 text-pure-black" />
            <span className="text-sm font-medium text-pure-black">
              {status.text}
            </span>
          </div>

          {/* Connection Details */}
          <div className="flex items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <span className="font-medium text-mono-700">Google Sheets:</span>
              <span className={systemStatus.sheetsConnected ? 'text-pure-black font-medium' : 'text-mono-500'}>
                {systemStatus.sheetsConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <span className="font-medium text-mono-700">Gemini API:</span>
              <span className={
                systemStatus.geminiApiStatus === 'connected' ? 'text-pure-black font-medium' : 'text-mono-500'
              }>
                {systemStatus.geminiApiStatus === 'connected' ? 'Connected' :
                  systemStatus.geminiApiStatus === 'error' ? 'Error' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>

        {/* Metrics */}
        <div className="flex items-center space-x-8 text-sm">
          <div className="text-right">
            <div className="text-2xl font-light text-pure-black tabular-nums">
              {systemStatus.totalOrders.toLocaleString()}
            </div>
            <div className="text-xs text-mono-600 mt-0.5 uppercase tracking-wide">
              Orders • {systemStatus.activeOrchestrators} Active
            </div>
          </div>

          <div className="h-12 w-px bg-mono-200"></div>

          <div className="text-right">
            <div className="text-sm font-medium text-pure-black">Last Sync</div>
            <div className="text-xs text-mono-600 mt-0.5">
              {formatDistanceToNow(systemStatus.lastSync, { addSuffix: true })}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default SystemStatus;