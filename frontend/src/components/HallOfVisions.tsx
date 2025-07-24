// --- START OF FILE src/components/HallOfVisions.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useVentureStore } from '@/store/ventureStore';

/**
 * HallOfVisions: Displays the 10 AI-generated business "Vision" cards for the user to choose from.
 */
export default function HallOfVisions() {
  // SAGA LOGIC: Get the generated visions and the 'chooseVision' function from the store.
  const visions = useVentureStore((state) => state.visions);
  const chooseVision = useVentureStore((state) => state.chooseVision);
  const error = useVentureStore((state) => state.error);

  if (error) {
    return <div className="text-center p-8 text-red-400">{error}</div>;
  }

  if (!visions || visions.length === 0) {
    return <div className="text-center p-8">The mists are thick... Saga could not divine any visions for this topic.</div>;
  }

  return (
    <motion.div
      key="hall-of-visions"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Hall of Visions
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark max-w-2xl mx-auto">
          Ten possible futures have been foreseen. Each is a seed of a potential empire.
          <br />
          Choose the path you wish to walk.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {visions.map((vision, index) => (
          <motion.div
            key={vision.prophecy_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <button
              onClick={() => chooseVision(vision.prophecy_id)}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300 group"
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-serif text-2xl font-bold text-saga-primary mb-2 group-hover:text-saga-secondary transition-colors">
                  {vision.title}
                </h3>
                <span className="font-mono text-xs bg-saga-bg px-2 py-1 rounded-full text-saga-text-dark whitespace-nowrap">
                   {vision.business_model}
                </span>
              </div>
              <p className="text-saga-text-light mb-4">
                {vision.one_line_pitch}
              </p>
              <p className="text-xs text-saga-text-dark">
                Evidence: <span className="font-semibold">{vision.evidence_tag}</span>
              </p>
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/HallOfVisions.tsx ---