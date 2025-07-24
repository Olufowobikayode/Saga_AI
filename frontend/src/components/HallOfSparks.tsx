// --- START OF FILE src/components/HallOfSparks.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useContentStore } from '@/store/contentStore';

/**
 * HallOfSparks: Displays the 5 AI-generated "Content Spark" cards for the user to choose from.
 */
export default function HallOfSparks() {
  // SAGA LOGIC: Get the generated sparks and the 'chooseSpark' function from the store.
  const sparks = useContentStore((state) => state.sparks);
  const chooseSpark = useContentStore((state) => state.chooseSpark);
  const tacticalInterest = useContentStore((state) => state.tacticalInterest);

  if (!sparks || sparks.length === 0) {
    return <div className="text-center p-8">The threads of fate are tangled... Saga could not divine any sparks for this topic.</div>;
  }

  return (
    <motion.div
      key="hall-of-sparks"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Threads of Inspiration
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Five potential sagas have been sparked from the topic of "<span className="text-saga-secondary">{tacticalInterest}</span>". Choose one to weave into a masterpiece.
        </p>
      </header>

      <div className="space-y-6">
        {sparks.map((spark, index) => (
          <motion.div
            key={spark.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <button
              onClick={() => chooseSpark(spark.id)}
              className="w-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary transition-all duration-300 group"
            >
              <h3 className="font-serif text-2xl font-bold text-saga-primary mb-2 group-hover:text-saga-secondary transition-colors">
                {spark.title}
              </h3>
              <p className="text-saga-text-dark mb-3">
                {spark.description}
              </p>
              <span className="font-mono text-sm bg-saga-bg px-2 py-1 rounded-md text-saga-primary">
                Suggested Format: {spark.format_suggestion}
              </span>
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/HallOfSparks.tsx ---