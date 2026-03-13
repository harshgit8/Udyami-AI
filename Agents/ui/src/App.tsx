import React from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import SystemStatus from './components/SystemStatus';
import OrchestratorGrid from './components/OrchestratorGrid';
import LiveExecution from './components/LiveExecution';
import LatestResults from './components/LatestResults';
import { OrchestratorProvider } from './context/OrchestratorContext';

function App() {
  return (
    <OrchestratorProvider>
      <div className="min-h-screen bg-pure-white font-system">
        <Header />

        <main className="max-w-7xl mx-auto px-8 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-8"
          >
            <SystemStatus />
            <OrchestratorGrid />
            <LiveExecution />
            <LatestResults />
          </motion.div>
        </main>
      </div>
    </OrchestratorProvider>
  );
}

export default App;