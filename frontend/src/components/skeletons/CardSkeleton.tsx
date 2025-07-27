// --- START OF NEW FILE src/components/skeletons/CardSkeleton.tsx ---
'use client';

import React from 'react';

/**
 * A simple, reusable skeleton component that shows a pulsing, grey placeholder.
 * It's used as a building block for more complex skeleton layouts.
 */
export default function CardSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={`
        bg-saga-surface p-6 rounded-lg border border-white/10
        animate-pulse 
        ${className}
      `}
    >
      <div className="space-y-4">
        {/* Placeholder for a title */}
        <div className="h-6 bg-saga-bg rounded w-3/4"></div>
        {/* Placeholder for content lines */}
        <div className="h-4 bg-saga-bg rounded w-full"></div>
        <div className="h-4 bg-saga-bg rounded w-5/6"></div>
        {/* Placeholder for a tag or button */}
        <div className="h-8 bg-saga-bg rounded w-1/3 pt-2"></div>
      </div>
    </div>
  );
}
// --- END OF NEW FILE src/components/skeletons/CardSkeleton.tsx ---