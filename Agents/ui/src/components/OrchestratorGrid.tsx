import React from 'react';
import { motion } from 'framer-motion';
import OrchestratorCard from './OrchestratorCard';
import { useOrchestrator } from '../context/OrchestratorContext';

const orchestratorConfigs = [
  {
    type: 'production' as const,
    title: 'Production',
    description: 'Schedule manufacturing orders',
    icon: '🏭',
  },
  {
    type: 'invoices' as const,
    title: 'Invoices',
    description: 'Generate tax-compliant invoices',
    icon: '📄',
  },
  {
    type: 'quality' as const,
    title: 'Quality',
    description: 'Inspect production batches',
    icon: '🔍',
  },
  {
    type: 'quotations' as const,
    title: 'Quotations',
    description: 'Generate customer quotes',
    icon: '💰',
  },
  {
    type: 'rnd' as const,
    title: 'R&D',
    description: 'Design material formulations',
    icon: '🧪',
  },
];

const OrchestratorGrid: React.FC = () => {
  const { orchestrators } = useOrchestrator();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6"
    >
      {orchestratorConfigs.map((config, index) => (
        <motion.div
          key={config.type}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 * index }}
        >
          <OrchestratorCard
            config={config}
            state={orchestrators[config.type]}
          />
        </motion.div>
      ))}
    </motion.div>
  );
};

export default OrchestratorGrid;