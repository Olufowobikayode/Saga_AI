// --- START OF FILE src/components/HallOfVisions.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useVentureStore } from '@/store/ventureStore';
import { useSagaStore } from '@/store/sagaStore';

/**
 * HallOfVisions: Displays the 10 AI-generated "Vision Cards" for the user to choose from.
 */
export default function HallOfVisions() {
  const { visions, chooseVision, error } = useVentureStore();
  const interest = useSagaStore((state) => state.brief.interest);

  if (error) {
    return <div className="text-center p-8 text-red-400">{error}</div>;
  }
  
  if (!visions || visions.length === 0) {
    return <div className="text-center p-8">The mists are thick... Saga could not divine any visions for this quest.</div>;
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
        <p className="mt-4 text-lg text-saga-text-dark">
          Ten potential futures for the interest of "<span className="text-saga-secondary">{interest}</span>" have been revealed. Choose one to forge into a reality.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {visions.map((vision, index) => (
          <motion.div
            key={vision.prophecy_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.05 * index }}
          >
            <button
              onClick={() => chooseVision(vision.prophecy_id)}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary transition-all duration-300 group"
            >
              <h3 className="font-serif text-2xl font-bold text-saga-primary mb-2 group-hover:text-saga-secondary transition-colors">
                {vision.title}
              </h3>
              <p className="text-saga-text-light font-semibold mb-3">
                {vision.one_line_pitch}
              </p>
              <div className="text-sm text-saga-text-dark flex justify-between items-center">
                <span className="font-mono bg-saga-bg px-2 py-1 rounded-md text-saga-primary">
                  {vision.business_model}
                </span>
                <span className="italic">
                  Inspired by: {vision.evidence_tag}
                </span>
              </div>
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/HallOfVisions.tsx ---