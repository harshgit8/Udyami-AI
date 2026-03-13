import React from 'react';
import { motion } from 'framer-motion';
import { PlayIcon, StopIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/solid';
import { useOrchestrator } from '../context/OrchestratorContext';
import { OrchestratorState, OrchestratorType } from '../types';

interface OrchestratorCardProps {
  config: {
    type: OrchestratorType;
    title: string;
    description: string;
    icon: string;
  };
  state: OrchestratorState;
}

const OrchestratorCard: React.FC<OrchestratorCardProps> = ({ config, state }) => {
  const { runOrchestrator, stopOrchestrator } = useOrchestrator();

  const getStatusInfo = () => {
    switch (state.status) {
      case 'idle':
        return {
          icon: PlayIcon,
          text: 'Ready',
          canRun: true,
        };
      case 'running':
        return {
          icon: StopIcon,
          text: 'Running',
          canRun: false,
        };
      case 'completed':
        return {
          icon: CheckCircleIcon,
          text: 'Completed',
          canRun: true,
        };
      case 'error':
        return {
          icon: ExclamationTriangleIcon,
          text: 'Error',
          canRun: true,
        };
      case 'pending':
        return {
          icon: ExclamationTriangleIcon,
          text: 'Pending',
          canRun: true,
        };
      default:
        return {
          icon: PlayIcon,
          text: 'Ready',
          canRun: true,
        };
    }
  };

  const statusInfo = getStatusInfo();
  const StatusIcon = statusInfo.icon;

  const handleAction = () => {
    if (state.status === 'running') {
      stopOrchestrator(config.type);
    } else {
      runOrchestrator(config.type);
    }
  };

  const getMetricValue = () => {
    switch (config.type) {
      case 'production':
        return '1,208 orders';
      case 'invoices':
        return '5 requests';
      case 'quality':
        return '3 batches';
      case 'quotations':
        return '12 requests';
      case 'rnd':
        return '2 formulations';
      default:
        return '0 items';
    }
  };

  return (
    <motion.div
      whileHover={{ y: -2, boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)' }}
      whileTap={{ scale: 0.99 }}
      className="bg-pure-white border border-mono-200 rounded-lg p-6 shadow-sm transition-all duration-150 cursor-pointer group hover:border-mono-300"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="w-11 h-11 bg-pure-black rounded-md flex items-center justify-center text-pure-white text-xl">
          {config.icon}
        </div>
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-mono-100 text-mono-900">
          <StatusIcon className="w-3.5 h-3.5" />
          <span>{statusInfo.text}</span>
        </div>
      </div>

      {/* Content */}
      <div className="mb-6">
        <h3 className="text-base font-semibold text-pure-black tracking-tight mb-1">
          {config.title}
        </h3>
        <p className="text-sm text-mono-600 mb-4 leading-relaxed">
          {config.description}
        </p>
        <div className="text-3xl font-light text-pure-black tabular-nums">
          {getMetricValue()}
        </div>
      </div>

      {/* Progress Bar (only show when running) */}
      {state.status === 'running' && (
        <div className="mb-5">
          <div className="flex items-center justify-between text-xs text-mono-700 mb-2 font-medium">
            <span className="truncate flex-1 mr-4">{state.currentStep}</span>
            <span className="tabular-nums">{Math.round(state.progress)}%</span>
          </div>
          <div className="progress-bar">
            <motion.div
              className="progress-fill"
              initial={{ width: 0 }}
              animate={{ width: `${state.progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <div className="text-xs text-mono-500 mt-1.5">
            Step {state.completedSteps} of {state.totalSteps}
          </div>
        </div>
      )}

      {/* Error Message */}
      {state.status === 'error' && state.error && (
        <div className="mb-4 p-3 bg-mono-50 border border-mono-300 rounded-md">
          <p className="text-xs text-mono-900">{state.error}</p>
        </div>
      )}

      {/* Action Button */}
      <motion.button
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        onClick={handleAction}
        disabled={!statusInfo.canRun && state.status !== 'running'}
        className={`w-full py-2.5 px-4 rounded-md font-medium text-sm transition-all duration-150 flex items-center justify-center space-x-2 ${state.status === 'running'
          ? 'bg-pure-black text-pure-white hover:bg-mono-900'
          : 'bg-pure-black text-pure-white hover:bg-mono-900 disabled:bg-mono-200 disabled:text-mono-500 disabled:cursor-not-allowed'
          }`}
      >
        {state.status === 'running' ? (
          <>
            <StopIcon className="w-4 h-4" />
            <span>Stop</span>
          </>
        ) : (
          <>
            <PlayIcon className="w-4 h-4" />
            <span>Run</span>
          </>
        )}
      </motion.button>
    </motion.div>
  );
};

export default OrchestratorCard;