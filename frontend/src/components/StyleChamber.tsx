// --- START OF REFACTORED FILE frontend/src/components/StyleChamber.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { usePodStore } from '@/store/podStore';
import { useSession } from '@/hooks/useSession'; // <-- 1. IMPORT HOOK
// NEW: Importing the centralized data
import { podStyles } from '@/lib/podOptions';

/**
 * StyleChamber: Allows the user to select the artistic style for their POD niche.
 */
export default function StyleChamber() {
  const { nicheInterest, huntOpportunities } = usePodStore();
  
  // --- 2. USE SESSION HOOK ---
  const { sessionId, isLoading: isSessionLoading } = useSession();

  const handleStyleSelection = (styleId: string) => {
    if (isSessionLoading || !sessionId) {
        alert("Session is not yet ready. Please wait a moment.");
        return;
    }
    // --- 3. PASS SESSION ID TO STORE ACTION ---
    huntOpportunities(styleId, sessionId);
  };

  return (
    <motion.div
      key="style-chamber"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          Choose Your Artistic Style
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark max-w-2xl mx-auto">
          The Anvil is ready to forge artifacts for the niche of "<span className="text-saga-secondary">{nicheInterest}</span>".
          <br />
          Select the creative lens through which Saga shall see the opportunities.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {/* Now mapping over the imported podStyles data */}
        {podStyles.map((option, index) => (
          <motion.div
            key={option.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * index }}
          >
            <button
              onClick={() => handleStyleSelection(option.id)}
              disabled={isSessionLoading}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed"
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
// --- END OF REFACTORED FILE frontend/src/components/StyleChamber.tsx ---