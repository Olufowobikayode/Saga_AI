// --- START OF NEW FILE src/components/skeletons/BlueprintScrollSkeleton.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';

/**
 * A reusable component for a single section within the blueprint skeleton.
 */
const SectionSkeleton = () => (
    <div className="bg-saga-bg p-6 rounded-lg border border-saga-surface">
        {/* Placeholder for section title */}
        <div className="h-8 bg-saga-surface rounded w-1/3 mb-4"></div>
        {/* Placeholder for content lines */}
        <div className="space-y-3">
            <div className="h-4 bg-saga-surface rounded w-full"></div>
            <div className="h-4 bg-saga-surface rounded w-5/6"></div>
            <div className="h-4 bg-saga-surface rounded w-3/4"></div>
        </div>
    </div>
);


/**
 * A skeleton loader that mimics the layout of the BlueprintScroll component.
 * It displays placeholders for the header and several content sections.
 */
export default function BlueprintScrollSkeleton() {
  return (
    <motion.div
      key="blueprint-scroll-skeleton"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1, transition: { delay: 0.2 } }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12 animate-pulse">
        {/* Placeholder for header */}
        <div className="h-12 bg-saga-surface rounded-lg w-3/4 mx-auto"></div>
        <div className="h-6 bg-saga-surface rounded-lg w-1/2 mx-auto mt-4"></div>
      </header>
      
      <div className="bg-saga-surface p-6 md:p-8 rounded-lg border border-white/10 shadow-lg space-y-6 animate-pulse">
        {/* Mimic the multiple sections of the real component */}
        <SectionSkeleton />
        <SectionSkeleton />
        <SectionSkeleton />
      </div>
    </motion.div>
  );
}
// --- END OF NEW FILE src/components/skeletons/BlueprintScrollSkeleton.tsx ---