// --- START OF FILE src/components/HallOfScrutiny.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useCommerceStore } from '@/store/commerceStore';

// SAGA UI: Defining the data for the three audit type cards.
const auditOptions = [
  {
    id: 'Account Audit',
    title: "Perform an Account Audit",
    description: "Analyze your financial statements to find profit leaks and opportunities for investment.",
    icon: "💰"
  },
  {
    id: 'Store Audit',
    title: "Perform a Store Audit",
    description: "Saga will scrutinize your store's content and compare it against top competitors.",
    icon: "🔍"
  },
  {
    id: 'Account Prediction',
    title: "Divine an Account Prediction",
    description: "Synthesize both financial and market data to prophesize your future outcomes.",
    icon: "🔮"
  }
];

/**
 * HallOfScrutiny: Displays the three audit types for the user to choose from.
 */
export default function HallOfScrutiny() {
  // SAGA LOGIC: The 'chooseProphecy' rite is multi-purpose. Here it sets the sub-type.
  // We will need to upgrade the store to handle this choice. For now, this is the UI.
  // A better name for this in the store might be 'chooseSubProphecy'.
  const chooseSubProphecy = (subType: string) => {
      console.log(`Sub-prophecy chosen: ${subType}`);
      // This will call a new function in the store to set the audit type and proceed.
  };

  return (
    <motion.div
      key="hall-of-scrutiny"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl font-bold text-white">
          The Hall of Scrutiny
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Choose the lens through which Saga shall conduct her audit.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {auditOptions.map((option, index) => (
          <motion.div
            key={option.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * index }}
          >
            <button
              onClick={() => chooseSubProphecy(option.id)}
              className="w-full h-full bg-saga-surface p-8 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300 group"
            >
              <div className="text-5xl mb-4">{option.icon}</div>
              <h3 className="font-serif text-2xl font-bold text-saga-primary mb-2 group-hover:text-saga-secondary transition-colors">
                {option.title}
              </h3>
              <p className="text-saga-text-dark leading-relaxed">
                {option.description}
              </p>
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/HallOfScrutiny.tsx ---