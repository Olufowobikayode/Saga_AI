// --- START OF REFACTORED FILE frontend/src/components/ScribesChamber.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';
import { useSession } from '@/hooks/useSession'; // <-- 1. IMPORT HOOK

// SAGA UI: Defining the data for our length selection cards.
const lengthOptions = [
  {
    id: 'Short',
    title: "Short & Punchy",
    description: "Ideal for social media feeds, quick ads, and capturing immediate attention.",
    icon: "⚡"
  },
  {
    id: 'Medium',
    title: "Medium & Detailed",
    description: "Perfect for email bodies, product descriptions, and informative posts.",
    icon: "📄"
  },
  {
    id: 'Long',
    title: "Long & Persuasive",
    description: "Best for landing pages, detailed affiliate reviews, or comprehensive threads.",
    icon: "📜"
  }
];

/**
 * ScribesChamber: A component that allows the user to select the desired length
 * for their text-based marketing asset.
 */
export default function ScribesChamber() {
  const chosenAssetType = useMarketingStore((state) => state.chosenAssetType);
  const chooseLength = useMarketingStore((state) => state.chooseLength);
  
  // -- 2. USE SESSION HOOK ---
  const { sessionId, isLoading: isSessionLoading } = useSession();

  const handleLengthSelection = (lengthId: string) => {
    if (isSessionLoading || !sessionId) {
        alert("Session is not yet ready. Please wait a moment.");
        return;
    }
    // --- 3. PASS SESSION ID TO STORE ACTION ---
    chooseLength(lengthId, sessionId);
  };

  return (
    <motion.div
      key="scribes-chamber"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          Choose the Scroll's Length
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          How shall the saga of your <span className="text-saga-secondary">{chosenAssetType}</span> be told?
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {lengthOptions.map((option, index) => (
          <motion.div
            key={option.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <button
              onClick={() => handleLengthSelection(option.id)}
              disabled={isSessionLoading}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="text-4xl mb-4">{option.icon}</div>
              <h3 className="font-serif text-2xl font-bold text-saga-secondary mb-2">
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
// --- END OF REFACTORED FILE frontend/src/components/ScribesChamber.tsx ---