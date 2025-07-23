// --- START OF FILE src/components/HallOfProphecies.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';

// SAGA UI: Defining the data for our tactical stack cards.
// This matches the names we decided upon.
const tacticalStacks = [
  {
    id: 'marketing',
    title: "The Skald's Forge",
    description: "Weave Words of Power: Ads, Funnels, & Persuasion",
    icon: "🔥"
  },
  {
    id: 'content',
    title: "The Weaver's Loom",
    description: "Craft Sagas for Any Realm: Posts, Blogs, & Comments",
    icon: "🕸️"
  },
  {
    id: 'new_ventures',
    title: "The Seer's Spire",
    description: "Gaze Into What May Be: Discover & Plan New Ventures",
    icon: "🔮"
  },
  {
    id: 'pod',
    title: "The Artisan's Anvil",
    description: "Forge Designs of Legend: Print-on-Demand Opportunities",
    icon: "⚒️"
  },
  {
    id: 'commerce',
    title: "The Merchant's Ledger",
    description: "Master the Flow of Coin: Audits, Arbitrage, & Product Routes",
    icon: "💰"
  }
];

/**
 * HallOfProphecies: The main results screen after the Grand Strategy is divined.
 * It displays the available tactical stacks as a series of clickable cards.
 */
export default function HallOfProphecies() {
  // SAGA LOGIC: We get the 'resetSaga' function to allow the user to start over.
  const resetSaga = useSagaStore((state) => state.resetSaga);

  const handleCardClick = (stackId: string) => {
    console.log(`Entering the ${stackId} prophecy...`);
    // In the future, this will navigate to the specific page for that stack.
  };

  return (
    <motion.div
      key="prophecies"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }} // A smooth, elegant ease.
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Grand Strategy is Forged
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          The path is revealed. Now, choose your next action.
        </p>
      </header>

      {/* 
        SAGA UI: A container that will scroll horizontally on small screens,
        and display as a centered grid on larger screens.
      */}
      <div className="flex gap-8 pb-8 overflow-x-auto md:flex-wrap md:justify-center md:overflow-x-visible">
        {tacticalStacks.map((stack, index) => (
          <motion.div
            key={stack.id}
            className="flex-shrink-0 w-72" // Ensures cards have a fixed width on mobile
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
          >
            <button
              onClick={() => handleCardClick(stack.id)}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300"
            >
              <div className="text-4xl mb-4">{stack.icon}</div>
              <h3 className="font-serif text-2xl font-bold text-saga-secondary mb-2">
                {stack.title}
              </h3>
              <p className="text-saga-text-dark leading-relaxed">
                {stack.description}
              </p>
            </button>
          </motion.div>
        ))}
      </div>

      {/* Reset Button to start a new consultation */}
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
// --- END OF FILE src/components/HallOfProphecies.tsx ---