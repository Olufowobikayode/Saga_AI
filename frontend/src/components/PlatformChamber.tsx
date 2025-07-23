// --- START OF FILE src/components/PlatformChamber.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';

// SAGA UI: Defining the data for our platform selection cards.
const platformOptions = [
  {
    id: 'Netlify Drop',
    title: "Netlify Drop",
    description: "The fastest way to deploy. Simply drag and drop your file to go live.",
    icon: "🚀"
  },
  {
    id: 'Google Sites',
    title: "Google Sites",
    description: "A free and simple website builder integrated with your Google account.",
    icon: "🇬"
  },
  {
    id: 'GitHub Pages',
    title: "GitHub Pages",
    description: "Host directly from a GitHub repository. Ideal for developers.",
    icon: "🐙"
  },
  {
    id: 'Other',
    title: "Other / Manual",
    description: "Receive general instructions for uploading to any web hosting provider.",
    icon: "🌐"
  }
];

/**
 * PlatformChamber: A component that allows the user to select their desired
 * hosting platform for HTML-based assets.
 */
export default function PlatformChamber() {
  // SAGA LOGIC: Get the necessary state and functions from the store.
  const chosenAssetType = useMarketingStore((state) => state.chosenAssetType);
  const choosePlatform = useMarketingStore((state) => state.choosePlatform);

  return (
    <motion.div
      key="platform-chamber"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          Choose the Realm of Deployment
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Where shall the saga of your <span className="text-saga-secondary">{chosenAssetType}</span> be inscribed upon the web?
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {platformOptions.map((option, index) => (
          <motion.div
            key={option.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <button
              onClick={() => choosePlatform(option.id)}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300"
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
// --- END OF FILE src/components/PlatformChamber.tsx ---