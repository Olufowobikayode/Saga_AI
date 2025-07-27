// --- START OF NEW FILE src/components/skeletons/HallOfVisionsSkeleton.tsx ---
'use client';

import React from 'react';
import CardSkeleton from './CardSkeleton';
import { motion } from 'framer-motion';

/**
 * A skeleton loader that mimics the layout of the HallOfVisions component.
 * It displays a grid of pulsing placeholders to improve perceived performance.
 */
export default function HallOfVisionsSkeleton() {
  return (
    <motion.div
      key="hall-of-visions-skeleton"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1, transition: { delay: 0.2 } }} // Slight delay to prevent flashing on fast loads
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        {/* Placeholder for header */}
        <div className="h-12 bg-saga-surface rounded-lg w-2/3 mx-auto animate-pulse"></div>
        <div className="h-6 bg-saga-surface rounded-lg w-1/2 mx-auto mt-4 animate-pulse"></div>
      </header>
      
      {/* Mimic the 2-column grid of the real component */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Create an array of 6 items to map over, generating 6 skeleton cards */}
        {Array.from({ length: 6 }).map((_, index) => (
          <CardSkeleton key={index} />
        ))}
      </div>
    </motion.div>
  );
}
// --- END OF NEW FILE src/components/skeletons/HallOfVisionsSkeleton.tsx ---