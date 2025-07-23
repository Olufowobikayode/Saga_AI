// --- START OF FILE src/components/HallOfAngles.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';

// SAGA UI: CORRECTED list of Asset Type cards, now including Email Copy.
const assetTypes = [
  {
    id: 'Ad Copy',
    title: "Ad Copy",
    description: "Forge persuasive copy for social media and search engine ads.",
    icon: "🎯"
  },
  {
    id: 'Email Copy',
    title: "Email Copy",
    description: "Compose high-open-rate emails for newsletters and campaigns.",
    icon: "✉️"
  },
  {
    id: 'Affiliate Copy',
    title: "Affiliate Copy",
    description: "Craft compelling messages for your partners to share.",
    icon: "🤝"
  },
  {
    id: 'Funnel Page',
    title: "Funnel Page",
    description: "Generate the complete HTML for a high-converting funnel page.",
    icon: "🌊"
  },
  {
    id: 'Landing Page',
    title: "Landing Page",
    description: "Create the full HTML for a beautiful, persuasive landing page.",
    icon: "🏠"
  },
  {
    id: 'Affiliate Review',
    title: "Affiliate Review",
    description: "Produce authentic, trustworthy reviews to promote affiliate products.",
    icon: "⭐"
  }
];

/**
 * HallOfAngles: Displays the available marketing asset types for the user to choose from.
 * This is the second major decision point in the Skald's Forge.
 */
export default function HallOfAngles() {
  const angles = useMarketingStore((state) => state.angles);

  const handleCardClick = (assetType: string) => {
    console.log(`Selected asset type: ${assetType}`);
    console.log('Available angles from backend:', angles);
    // In the next step, we will implement the logic to select a strategic angle and call the store.
  };

  return (
    <motion.div
      key="hall-of-angles"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Strategic Angles are Revealed
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          The core strategies have been forged. Now, choose the form your weapon shall take.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {assetTypes.map((asset, index) => (
          <motion.div
            key={asset.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <button
              onClick={() => handleCardClick(asset.id)}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300"
            >
              <div className="text-4xl mb-4">{asset.icon}</div>
              <h3 className="font-serif text-2xl font-bold text-saga-secondary mb-2">
                {asset.title}
              </h3>
              <p className="text-saga-text-dark leading-relaxed">
                {asset.description}
              </p>
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/HallOfAngles.tsx ---