// --- START OF FILE src/components/ScribesChamber.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';

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

// SAGA LOGIC: Defining the properties for this component.
// It needs to know which asset type it's generating a length for (e.g., "Ad Copy").
interface ScribesChamberProps {
  assetType: string;
  onLengthSelect: (length: string) => void; // A function to call when a length is chosen.
}

/**
 * ScribesChamber: A component that allows the user to select the desired length
 * for their marketing asset.
 */
export default function ScribesChamber({ assetType, onLengthSelect }: ScribesChamberProps) {
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
          How shall the saga of your <span className="text-saga-secondary">{assetType}</span> be told?
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
              onClick={() => onLengthSelect(option.id)}
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
// --- END OF FILE src/components/ScribesChamber.tsx ---