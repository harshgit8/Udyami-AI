import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { DocumentTextIcon, GlobeAltIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/solid';
import { useOrchestrator } from '../context/OrchestratorContext';
import { orchestratorService } from '../services/orchestratorService';

interface ResultsData {
  production?: any;
  invoices?: any;
  quality?: any;
  quotations?: any;
  rnd?: any;
}

const LatestResults: React.FC = () => {
  const { orchestrators } = useOrchestrator();
  const [results, setResults] = useState<ResultsData>({});
  const [activeTab, setActiveTab] = useState<'production' | 'invoices' | 'quality' | 'quotations' | 'rnd'>('production');

  // Load results when orchestrators complete
  useEffect(() => {
    const loadResults = async () => {
      const newResults: ResultsData = {};

      for (const [type, state] of Object.entries(orchestrators)) {
        if (state.status === 'completed' && state.results) {
          try {
            const data = await orchestratorService.getResults(type as any);
            newResults[type as keyof ResultsData] = data;
          } catch (error) {
            // Error loading results
          }
        }
      }

      setResults(newResults);
    };

    loadResults();
  }, [orchestrators]);

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'PROCEED':
      case 'ACCEPT':
        return <CheckCircleIcon className="w-4 h-4 text-pure-black" />;
      case 'DELAY':
      case 'CONDITIONAL_ACCEPT':
        return <ExclamationTriangleIcon className="w-4 h-4 text-mono-600" />;
      case 'REJECT':
        return <XCircleIcon className="w-4 h-4 text-mono-700" />;
      default:
        return <div className="w-4 h-4 rounded-full bg-mono-300" />;
    }
  };

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'PROCEED':
      case 'ACCEPT':
        return 'text-pure-black font-semibold';
      case 'DELAY':
      case 'CONDITIONAL_ACCEPT':
        return 'text-mono-700 font-medium';
      case 'REJECT':
        return 'text-mono-800 font-medium';
      default:
        return 'text-mono-500';
    }
  };

  const getRiskScoreColor = (score: number) => {
    if (score <= 3) return 'bg-mono-100 text-pure-black border border-mono-200';
    if (score <= 6) return 'bg-mono-200 text-pure-black border border-mono-300';
    return 'bg-mono-300 text-pure-black border border-mono-400';
  };

  const renderProductionResults = () => {
    const data = results.production;
    if (!data || !data.decisions) return <div className="text-center text-mono-600 py-12">No production results available</div>;

    const summary = {
      scheduled: data.decisions.filter((d: any) => d.decision === 'PROCEED').length,
      delayed: data.decisions.filter((d: any) => d.decision === 'DELAY').length,
      rejected: data.decisions.filter((d: any) => d.decision === 'REJECT').length,
    };

    return (
      <div className="space-y-6">
        {/* Summary Cards - Ultra Clean */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-mono-50 border border-mono-200 rounded-lg p-5 text-center hover:shadow-md transition-shadow duration-150">
            <div className="text-4xl font-light text-pure-black tabular-nums mb-1">{summary.scheduled}</div>
            <div className="text-xs text-mono-600 uppercase tracking-wide font-medium">Scheduled</div>
          </div>
          <div className="bg-mono-100 border border-mono-200 rounded-lg p-5 text-center hover:shadow-md transition-shadow duration-150">
            <div className="text-4xl font-light text-pure-black tabular-nums mb-1">{summary.delayed}</div>
            <div className="text-xs text-mono-600 uppercase tracking-wide font-medium">Delayed</div>
          </div>
          <div className="bg-mono-200 border border-mono-300 rounded-lg p-5 text-center hover:shadow-md transition-shadow duration-150">
            <div className="text-4xl font-light text-pure-black tabular-nums mb-1">{summary.rejected}</div>
            <div className="text-xs text-mono-700 uppercase tracking-wide font-medium">Rejected</div>
          </div>
        </div>

        {/* Results Table - Minimal  & Clear */}
        <div className="bg-pure-white border border-mono-200 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-mono-50 border-b border-mono-200">
              <tr>
                <th className="px-5 py-3.5 text-left text-xs font-semibold text-mono-900 uppercase tracking-wide">Order</th>
                <th className="px-5 py-3.5 text-left text-xs font-semibold text-mono-900 uppercase tracking-wide">Decision</th>
                <th className="px-5 py-3.5 text-left text-xs font-semibold text-mono-900 uppercase tracking-wide">Risk</th>
                <th className="px-5 py-3.5 text-left text-xs font-semibold text-mono-900 uppercase tracking-wide">Schedule</th>
                <th className="px-5 py-3.5 text-left text-xs font-semibold text-mono-900 uppercase tracking-wide">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-mono-200">
              {data.decisions.slice(0, 10).map((decision: any, index: number) => (
                <motion.tr
                  key={decision.order_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.03 }}
                  className="hover:bg-mono-50 transition-colors duration-100"
                >
                  <td className="px-5 py-4 text-sm font-medium text-pure-black">
                    {decision.order_id}
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center space-x-2">
                      {getDecisionIcon(decision.decision)}
                      <span className={`text-sm ${getDecisionColor(decision.decision)}`}>
                        {decision.decision}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold tabular-nums ${getRiskScoreColor(decision.risk_score)}`}>
                      {decision.risk_score}/10
                    </span>
                  </td>
                  <td className="px-5 py-4 text-sm text-mono-900">
                    {decision.machine && decision.start_time ? (
                      <div>
                        <div className="font-medium">{decision.machine}</div>
                        <div className="text-xs text-mono-600 mt-0.5">
                          {new Date(decision.start_time).toLocaleDateString()} {new Date(decision.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    ) : (
                      <span className="text-mono-400">Not scheduled</span>
                    )}
                  </td>
                  <td className="px-5 py-4 text-sm text-mono-700 max-w-xs">
                    <div className="line-clamp-2">{decision.reason}</div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderGenericResults = (type: string) => {
    const data = results[type as keyof ResultsData];
    if (!data) return <div className="text-center text-macos-gray-500 py-8">No {type} results available</div>;

    return (
      <div className="bg-white border border-macos-gray-200 rounded-macos p-6">
        <div className="text-center text-macos-gray-500">
          <div className="text-4xl mb-4">📊</div>
          <h3 className="text-lg font-medium text-macos-gray-900 mb-2">
            {type.charAt(0).toUpperCase() + type.slice(1)} Results
          </h3>
          <p className="text-sm">
            Results are available in the generated reports and Google Sheets.
          </p>
        </div>
      </div>
    );
  };

  const tabs = [
    { id: 'production', label: 'Production', count: results.production?.decisions?.length || 0 },
    { id: 'invoices', label: 'Invoices', count: results.invoices?.length || 0 },
    { id: 'quality', label: 'Quality', count: results.quality?.length || 0 },
    { id: 'quotations', label: 'Quotations', count: results.quotations?.length || 0 },
    { id: 'rnd', label: 'R&D', count: results.rnd?.length || 0 },
  ];

  const hasAnyResults = Object.values(results).some(result => result);

  if (!hasAnyResults) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.2 }}
      className="bg-pure-white border border-mono-200 rounded-lg shadow-sm"
    >
      {/* Header */}
      <div className="px-8 py-5 border-b border-mono-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-pure-black tracking-tight">Latest Results</h2>
          <div className="flex items-center space-x-2">
            <button className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-mono-900 bg-pure-white border border-mono-200 rounded-md hover:bg-mono-50 hover:border-mono-300 transition-all duration-150">
              <DocumentTextIcon className="w-4 h-4 mr-2" />
              View Report
            </button>
            <button className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-mono-900 bg-pure-white border border-mono-200 rounded-md hover:bg-mono-50 hover:border-mono-300 transition-all duration-150">
              <GlobeAltIcon className="w-4 h-4 mr-2" />
              Open HTML
            </button>
            <button className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-mono-900 bg-pure-white border border-mono-200 rounded-md hover:bg-mono-50 hover:border-mono-300 transition-all duration-150">
              <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-8 py-4 border-b border-mono-200 bg-mono-50">
        <nav className="flex space-x-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-md transition-all duration-150 ${activeTab === tab.id
                  ? 'bg-pure-black text-pure-white shadow-sm'
                  : 'text-mono-700 hover:text-pure-black hover:bg-mono-100'
                }`}
            >
              <span>{tab.label}</span>
              {tab.count > 0 && (
                <span className={`px-2 py-0.5 text-xs font-semibold rounded-md tabular-nums ${activeTab === tab.id
                    ? 'bg-mono-900 text-pure-white'
                    : 'bg-mono-200 text-mono-900'
                  }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="p-8">
        {activeTab === 'production' ? renderProductionResults() : renderGenericResults(activeTab)}
      </div>
    </motion.div>
  );
};

export default LatestResults;