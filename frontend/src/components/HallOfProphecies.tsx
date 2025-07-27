// --- START OF REFACTORED FILE frontend/src/components/HallOfProphecies.tsx ---
'use client';

import React from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';
import GrandStrategyScroll from './GrandStrategyScroll'; // <-- 1. IMPORT THE NEW COMPONENT
import SagaButton from './SagaButton';

// Data for the tactical stack cards
const tacticalStacks = [
  { id: 'marketing', title: "The Skald's Forge", path: "/forge" },
  { id: 'content', title: "The Weaver's Loom", path: "/loom" },
  { id: 'new_ventures', title: "The Seer's Spire", path: "/spire" },
  { id: 'pod', title: "The Artisan's Anvil", path: "/anvil" },
  { id: 'commerce', title: "The Merchant's Ledger", path: "/ledger" }
];

/**
 * HallOfProphecies: This component now acts as a manager for the results screen.
 * It conditionally renders either the tactical hub or the detailed strategy scroll based on the store's status.
 */
export default function HallOfProphecies() {
  const { status, showStrategyScroll, showTacticalHub, resetSaga } = useSagaStore();

  // --- 2. CONDITIONAL RENDERING LOGIC ---
  if (status === 'prophesied_scroll') {
    return (
        <div>
            <GrandStrategyScroll />
            <div className="text-center mt-12">
                <button 
                    onClick={showTacticalHub}
                    className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors"
                >
                    ← View Tactical Options
                </button>
            </div>
        </div>
    );
  }

  // Default view is the tactical hub
  return (
    <motion.div
      key="prophecies-hub"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Grand Strategy is Forged
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          The path is revealed. View the full prophecy or choose a tactical tool to begin.
        </p>

        {/* --- 3. ADD THE "VIEW STRATEGY" BUTTON --- */}
        <div className="mt-8">
            <SagaButton onClick={showStrategyScroll}>
                View Full Strategy Scroll
            </SagaButton>
        </div>
      </header>
      
      <div className="border-t border-white/10 mt-12 pt-12">
        <h3 className="text-center font-serif text-3xl text-saga-primary mb-8">Tactical Gateways</h3>
        <div className="flex gap-8 pb-8 overflow-x-auto md:flex-wrap md:justify-center md:overflow-x-visible">
          {tacticalStacks.map((stack, index) => (
            <motion.div
              key={stack.id}
              className="flex-shrink-0 w-72"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
            >
              <Link href={stack.path} passHref>
                <div className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                           hover:border-saga-primary hover:scale-105 transition-all duration-300 cursor-pointer">
                  <h3 className="font-serif text-2xl font-bold text-saga-secondary mb-2">
                    {stack.title}
                  </h3>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="text-center mt-12">
        <button 
          onClick={resetSaga}
          className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors"
        >
          ← Begin a New Divination
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF REFACTORED FILE frontend/src/components/HallOfProphecies.tsx ---