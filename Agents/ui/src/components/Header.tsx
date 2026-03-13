import React from 'react';
import { motion } from 'framer-motion';
import { CogIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { useOrchestrator } from '../context/OrchestratorContext';

const Header: React.FC = () => {
  const { refreshStatus, syncSheets } = useOrchestrator();

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="bg-pure-white border-b border-mono-200"
    >
      <div className="max-w-7xl mx-auto px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-5">
            <div className="w-10 h-10 bg-pure-black rounded-md flex items-center justify-center">
              <svg className="w-6 h-6 text-pure-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-semibold text-pure-black tracking-tight">
                Manufacturing Orchestration
              </h1>
              <p className="text-sm text-mono-600 mt-0.5">
                AI-Powered Production Management System
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={syncSheets}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-mono-900 bg-pure-white border border-mono-200 rounded-md hover:bg-mono-50 hover:border-mono-300 transition-all duration-150"
            >
              <ArrowPathIcon className="w-4 h-4 mr-2" />
              Sync Sheets
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={refreshStatus}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-mono-900 bg-pure-white border border-mono-200 rounded-md hover:bg-mono-50 hover:border-mono-300 transition-all duration-150"
            >
              <CogIcon className="w-4 h-4 mr-2" />
              Settings
            </motion.button>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;