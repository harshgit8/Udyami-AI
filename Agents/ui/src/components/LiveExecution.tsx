import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircleIcon, ClockIcon, ExclamationCircleIcon } from '@heroicons/react/24/solid';
import { useOrchestrator } from '../context/OrchestratorContext';
import { OrchestratorType } from '../types';

const LiveExecution: React.FC = () => {
  const { orchestrators } = useOrchestrator();

  // Find the currently running orchestrator
  const runningOrchestrator = Object.values(orchestrators).find(
    (orchestrator) => orchestrator.status === 'running'
  );

  if (!runningOrchestrator) {
    return null;
  }

  const getOrchestratorTitle = (type: OrchestratorType) => {
    const titles = {
      production: 'Production Orchestrator',
      invoices: 'Invoice Generator',
      quality: 'Quality Inspector',
      quotations: 'Quotation Generator',
      rnd: 'R&D Formulator',
    };
    return titles[type];
  };

  const getSteps = (type: OrchestratorType) => {
    const steps = {
      production: [
        'Reading orders from Google Sheets',
        'Validating and cleaning orders',
        'Checking machine capacity',
        'Checking materials availability',
        'Analyzing deadlines',
        'Calculating setup times',
        'Structuring data for optimizer',
        'Running optimizer',
        'Generating reports',
      ],
      invoices: [
        'Reading invoice requests',
        'Processing invoices',
        'Writing results to sheets',
      ],
      quality: [
        'Reading inspection data',
        'Processing quality inspections',
        'Writing results to sheets',
      ],
      quotations: [
        'Reading quotation requests',
        'Processing quotations',
        'Writing results to sheets',
      ],
      rnd: [
        'Reading formulation requests',
        'Processing formulations',
        'Writing results to sheets',
      ],
    };
    return steps[type] || [];
  };

  const steps = getSteps(runningOrchestrator.type);
  const currentStepIndex = runningOrchestrator.completedSteps;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20, height: 0 }}
        animate={{ opacity: 1, y: 0, height: 'auto' }}
        exit={{ opacity: 0, y: -20, height: 0 }}
        transition={{ duration: 0.25 }}
        className="bg-mono-50 border border-mono-200 rounded-lg p-8 shadow-sm"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-2.5 h-2.5 bg-pure-black rounded-full animate-pulse-subtle"></div>
            <h2 className="text-lg font-semibold text-pure-black tracking-tight">
              {getOrchestratorTitle(runningOrchestrator.type)} - Running
            </h2>
          </div>
          <div className="text-sm text-mono-600">
            {runningOrchestrator.startTime && (
              <span>
                Started {new Date(runningOrchestrator.startTime).toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex items-center justify-between text-sm text-mono-900 font-medium mb-2">
            <span className="truncate flex-1 mr-4">{runningOrchestrator.currentStep}</span>
            <span className="font-mono tabular-nums">{Math.round(runningOrchestrator.progress)}%</span>
          </div>
          <div className="progress-bar h-1.5">
            <motion.div
              className="progress-fill h-full"
              initial={{ width: 0 }}
              animate={{ width: `${runningOrchestrator.progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
          <div className="flex items-center justify-between text-xs text-mono-600 mt-2">
            <span>Step {runningOrchestrator.completedSteps} of {runningOrchestrator.totalSteps}</span>
            <span>
              {runningOrchestrator.startTime && (
                <>
                  Elapsed: {Math.round((Date.now() - new Date(runningOrchestrator.startTime).getTime()) / 1000)}s
                </>
              )}
            </span>
          </div>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {steps.map((step, index) => {
            const isCompleted = index < currentStepIndex;
            const isCurrent = index === currentStepIndex;

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.25, delay: index * 0.03 }}
                className={`flex items-center space-x-3 p-3 rounded-md transition-all duration-150 ${isCompleted
                    ? 'bg-mono-100 border border-mono-300'
                    : isCurrent
                      ? 'bg-pure-white border border-pure-black'
                      : 'bg-pure-white border border-mono-200'
                  }`}
              >
                <div className="flex-shrink-0">
                  {isCompleted ? (
                    <CheckCircleIcon className="w-5 h-5 text-pure-black" />
                  ) : isCurrent ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    >
                      <ClockIcon className="w-5 h-5 text-pure-black" />
                    </motion.div>
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-mono-300"></div>
                  )}
                </div>
                <span
                  className={`text-sm font-medium ${isCompleted
                      ? 'text-mono-700'
                      : isCurrent
                        ? 'text-pure-black'
                        : 'text-mono-500'
                    }`}
                >
                  {step}
                </span>
              </motion.div>
            );
          })}
        </div>

        {/* Error Display */}
        {runningOrchestrator.error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-3 bg-mono-100 border border-mono-300 rounded-md flex items-start space-x-3"
          >
            <ExclamationCircleIcon className="w-5 h-5 text-pure-black flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-pure-black">Error occurred</p>
              <p className="text-sm text-mono-700 mt-1">{runningOrchestrator.error}</p>
            </div>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
};

export default LiveExecution;