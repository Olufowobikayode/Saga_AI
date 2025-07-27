// --- START OF NEW FILE src/components/GrandStrategyScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';

// SAGA UI: A reusable component for each of the "Three Great Sagas".
const SagaSection = ({ saga }: { saga: any }) => (
  <div className="bg-saga-bg p-6 rounded-lg border border-saga-surface">
    <h4 className="font-serif text-2xl text-saga-primary mb-3">{saga.saga_name}</h4>
    <p className="text-saga-text-dark mb-4">{saga.description}</p>
    <div className="border-t border-saga-primary/20 pt-4">
      <p className="text-sm font-semibold text-saga-text-light mb-1">Prime Directive:</p>
      <p className="text-saga-text-light italic">"{saga.prime_directive}"</p>
    </div>
  </div>
);

/**
 * GrandStrategyScroll: Displays the final, detailed Grand Strategy prophecy
 * in a user-friendly and visually appealing format.
 */
export default function GrandStrategyScroll() {
  const strategyData = useSagaStore((state) => state.strategyData);

  // Guard against rendering without data.
  if (!strategyData || !strategyData.prophecy) {
    return (
        <div className="text-center p-8 bg-saga-surface rounded-lg">
            <h2 className="font-serif text-3xl text-red-400 mb-4">The Vision is Faint</h2>
            <p className="text-saga-text-dark">Saga's prophecy has not yet been divined or has been lost to the ether. Please begin a new consultation.</p>
        </div>
    )
  }

  const {
    prophecy_title,
    divine_summary,
    target_soul_profile,
    the_three_great_sagas,
    first_commandment
  } = strategyData.prophecy;

  return (
    <motion.div
      key="grand-strategy-scroll"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: "easeOut" }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          {prophecy_title}
        </h2>
      </header>
      
      <div className="bg-saga-surface p-6 md:p-8 rounded-lg border border-white/10 shadow-lg space-y-8">

        {/* Divine Summary Section */}
        <div>
          <h3 className="font-serif text-3xl text-saga-secondary mb-4 border-b-2 border-saga-secondary/30 pb-3">Divine Summary</h3>
          <p className="text-saga-text-light text-lg leading-relaxed whitespace-pre-wrap">{divine_summary}</p>
        </div>
        
        {/* Target Soul Profile Section */}
        <div>
          <h3 className="font-serif text-3xl text-saga-secondary mb-4 border-b-2 border-saga-secondary/30 pb-3">Target Soul Profile</h3>
          <p className="text-saga-text-light text-lg leading-relaxed whitespace-pre-wrap">{target_soul_profile}</p>
        </div>

        {/* The Three Great Sagas Section */}
        <div>
          <h3 className="font-serif text-3xl text-saga-secondary mb-6 border-b-2 border-saga-secondary/30 pb-3">The Three Great Sagas</h3>
          <div className="space-y-6">
            {the_three_great_sagas.map((saga: any, index: number) => (
              <SagaSection key={index} saga={saga} />
            ))}
          </div>
        </div>
        
        {/* First Commandment Section */}
        <div className="bg-saga-primary text-saga-bg p-6 rounded-lg text-center">
            <h3 className="font-serif text-2xl font-bold mb-2">The First Commandment</h3>
            <p className="text-lg font-semibold">"{first_commandment}"</p>
        </div>

      </div>
    </motion.div>
  );
}
// --- END OF NEW FILE src/components/GrandStrategyScroll.tsx ---