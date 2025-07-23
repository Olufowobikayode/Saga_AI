// --- START OF FILE src/components/TextPlatformChamber.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';

// SAGA UI: Defining the data for our text/ad platform selection cards.
const platformOptions = [
  {
    id: 'Facebook',
    title: "Facebook / Instagram",
    description: "For broad audiences, community engagement, and visual storytelling.",
    icon: "👍"
  },
  {
    id: 'Google Ads',
    title: "Google Ads",
    description: "Capture high-intent users actively searching for your solution.",
    icon: "🇬"
  },
  {
    id: 'TikTok',
    title: "TikTok",
    description: "Engage a younger demographic with trend-driven, short-form video content.",
    icon: "🎵"
  },
  {
    id: 'LinkedIn',
    title: "LinkedIn",
    description: "Target professionals, B2B clients, and industry-specific roles.",
    icon: "💼"
  },
  {
    id: 'X (Twitter)',
    title: "X (formerly Twitter)",
    description: "For real-time conversation, news-jacking, and concise messaging.",
    icon: "🐦"
  },
  {
    id: 'Email',
    title: "Email Newsletter",
    description: "For direct, personal communication with your existing audience.",
    icon: "✉️"
  }
];

/**
 * TextPlatformChamber: A component that allows the user to select their desired
 * platform for text-based assets like Ad Copy.
 */
export default function TextPlatformChamber() {
  const chosenAssetType = useMarketingStore((state) => state.chosenAssetType);
  const choosePlatform = useMarketingStore((state) => state.choosePlatform);

  return (
    <motion.div
      key="text-platform-chamber"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          Choose the Realm of Proclamation
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Where shall the saga of your <span className="text-saga-secondary">{chosenAssetType}</span> be heard?
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
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
// --- END OF FILE src/components/TextPlatformChamber.tsx ---