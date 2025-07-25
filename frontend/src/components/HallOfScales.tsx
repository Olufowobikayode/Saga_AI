// --- START OF FILE src/components/HallOfScales.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useCommerceStore, ArbitrageMode } from '@/store/commerceStore';

// SAGA UI: Defining the data for the four arbitrage mode cards.
const arbitrageOptions = [
  {
    id: 'Saga_Buys_Saga_Sells',
    title: "Saga's Full Counsel",
    description: "Saga will divine both a low-cost realm to acquire a product AND a high-value realm in which to sell it.",
    icon: "🌌"
  },
  {
    id: 'Saga_Buys_User_Sells',
    title: "Divine the Source",
    description: "You know where to sell an item. Command Saga to find the most profitable realm from which to source it.",
    icon: "🔍"
  },
  {
    id: 'User_Buys_Saga_Sells',
    title: "Divine the Market",
    description: "You have a source for an item. Command Saga to find the highest-value realm in which to sell it.",
    icon: "📈"
  },
  {
    id: 'User_Buys_User_Sells',
    title: "Validate a Path",
    description: "You know both the source and the market. Command Saga to analyze the path and prophesize its profitability.",
    icon: "⚖️"
  }
];

/**
 * HallOfScales: Displays the four arbitrage modes for the user to choose from.
 */
export default function HallOfScales() {
  // SAGA LOGIC: Get the 'chooseArbitrageMode' rite from the store.
  const chooseArbitrageMode = useCommerceStore((state) => state.chooseArbitrageMode);

  return (
    <motion.div
      key="hall-of-scales"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl font-bold text-white">
          The Hall of Scales
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Weigh the paths of commerce and choose your method of arbitrage.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {arbitrageOptions.map((option, index) => (
          <motion.div
            key={option.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * index }}
          >
            <button
              onClick={() => chooseArbitrageMode(option.id as ArbitrageMode)}
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
// --- END OF FILE src/components/HallOfScales.tsx ---