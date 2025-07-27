// --- START OF NEW FILE src/components/ErrorMessage.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface ErrorMessageProps {
  error: string | null;
  onRetry?: () => void; // An optional function to allow the user to retry the action
}

/**
 * A standardized, themed component for displaying errors to the user.
 * It provides a clear message and an optional "Retry" action.
 */
export default function ErrorMessage({ error, onRetry }: ErrorMessageProps) {
  // If there's no error, render nothing.
  if (!error) {
    return null;
  }

  return (
    <motion.div
      className="bg-red-900/30 border border-red-500/50 text-red-300 p-6 rounded-lg mt-8 text-center"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex flex-col items-center">
        <div className="text-3xl mb-3">⚠️</div>
        <h3 className="font-serif text-xl font-bold mb-2">A Disturbance Was Detected</h3>
        <p className="text-sm max-w-md">
          {/* We display the error message from the store. */}
          {error}
        </p>
        
        {/* If an onRetry function was provided, render a "Retry" button. */}
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-4 bg-red-500/20 hover:bg-red-500/40 text-white font-bold py-2 px-4 rounded-lg transition-colors"
          >
            Retry Ritual
          </button>
        )}
      </div>
    </motion.div>
  );
}
// --- END OF NEW FILE src/components/ErrorMessage.tsx ---