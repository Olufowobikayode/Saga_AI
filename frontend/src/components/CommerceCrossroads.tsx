// --- START OF FILE src/components/CommerceCrossroads.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useCommerceStore, CommerceProphecyType } from '@/store/commerceStore';

// SAGA UI: Defining the data for the four great prophecy cards.
const prophecyOptions = [
  {
    id: 'Commerce Audit',
    title: "Commerce Audit",
    description: "Receive a divine audit of your store, accounts, or predict future outcomes based on your data.",
    icon: "📊"
  },
  {
    id: 'Arbitrage Paths',
    title: "Arbitrage Paths",
    description: "Unveil the hidden paths of profit. Discover opportunities to buy low and sell high across realms.",
    icon: "⚖️"
  },
  {
    id: 'Social Selling Saga',
    title: "Social Selling Saga",
    description: "Forge a complete battle plan for selling a product on social media, based on your profit goals.",
    icon: "📱"
  },
  {
    id: 'Product Route',
    title: "Product Route",
    description: "Let Saga divine a high-profit-margin product and reveal its complete route to market.",
    icon: "🗺️"
  }
];

/**
 * CommerceCrossroads: Displays the four main prophecy types for the user to choose from.
 * Each choice will invoke a sacred ritual.
 */
export default function CommerceCrossroads() {
  const chooseProphecy = useCommerceStore((state) => state.chooseProphecy);

  return (
    <motion.div
      key="commerce-crossroads"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl font-bold text-white">
          Choose Your Prophecy
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Select the commercial wisdom you seek from the Ledger. Each choice begins a new ritual.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {prophecyOptions.map((option, index) => (
          <motion.div
            key={option.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * index }}
          >
            <button
              onClick={() => chooseProphecy(option.id as CommerceProphecyType)}
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
// --- END OF FILE src/components/CommerceCrossroads.tsx ---