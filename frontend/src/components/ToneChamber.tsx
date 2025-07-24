// --- START OF FILE src/components/ToneChamber.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useContentStore } from '@/store/contentStore';

// SAGA UI: Defining the data for our tone/style selection cards.
const toneOptions = [
  {
    id: 'Educational',
    title: "Educational",
    description: "Write as a wise teacher. Provide value, facts, and clear instructions.",
    icon: "🎓"
  },
  {
    id: 'Engaging',
    title: "Engaging",
    description: "Write as a community leader. Ask questions and encourage discussion.",
    icon: "💬"
  },
  {
    id: 'Fun',
    title: "Fun & Witty",
    description: "Write as a clever skald. Use humor, wit, and playful language.",
    icon: "😂"
  },
  {
    id: 'Inspirational',
    title: "Inspirational",
    description: "Write as a visionary. Motivate and empower the audience with bold statements.",
    icon: "✨"
  },
  {
    id: 'Formal',
    title: "Formal & Professional",
    description: "Write as a royal scribe. Use formal language suitable for platforms like LinkedIn.",
    icon: "🖋️"
  }
];

/**
 * ToneChamber: Allows the user to select the writing style for their social post.
 */
export default function ToneChamber() {
  // SAGA LOGIC: Get the necessary state and function from the store.
  const chooseTone = useContentStore((state) => state.chooseTone);
  const chosenSpark = useContentStore((state) => state.chosenSpark);

  return (
    <motion.div
      key="tone-chamber"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          Choose the Voice of the Saga
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          How shall the story of "<span className="text-saga-secondary">{chosenSpark?.title}</span>" be told?
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {toneOptions.map((option, index) => (
          <motion.div
            key={option.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * index }}
          >
            <button
              onClick={() => chooseTone(option.id)}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300 group"
            >
              <div className="text-4xl mb-4">{option.icon}</div>
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
// --- END OF FILE src/components/ToneChamber.tsx ---