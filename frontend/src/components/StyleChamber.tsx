// --- START OF FILE src/components/StyleChamber.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { usePodStore } from '@/store/podStore';

// SAGA UI: Defining the data for our artistic style selection cards.
const styleOptions = [
  {
    id: 'Vintage',
    title: "Vintage / Retro",
    description: "Classic, distressed, and nostalgic designs with a timeless appeal.",
    icon: "📜"
  },
  {
    id: 'Minimalist',
    title: "Minimalist / Line Art",
    description: "Clean, simple, and elegant designs using minimal lines and shapes.",
    icon: "✒️"
  },
  {
    id: 'Photorealistic',
    title: "Photorealistic",
    description: "Hyper-detailed and lifelike designs that mimic high-quality photographs.",
    icon: "📸"
  },
  {
    id: 'Abstract',
    title: "Abstract / Geometric",
    description: "Artistic designs using shapes, forms, colors, and textures.",
    icon: "🎨"
  },
  {
    id: 'Cartoon / Anime',
    title: "Cartoon / Anime",
    description: "Playful, animated, and stylized designs inspired by popular media.",
    icon: "😊"
  },
  {
    id: 'Cyberpunk',
    title: "Cyberpunk / Sci-Fi",
    description: "Futuristic, high-tech designs with neon colors and dystopian themes.",
    icon: "🤖"
  }
];

/**
 * StyleChamber: Allows the user to select the artistic style for their POD niche.
 */
export default function StyleChamber() {
  // SAGA LOGIC: Get the necessary state and function from the store.
  const { nicheInterest, huntOpportunities } = usePodStore();

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
        {styleOptions.map((option, index) => (
          <motion.div
            key={option.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * index }}
          >
            <button
              onClick={() => huntOpportunities(option.id)}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300 group"
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
// --- END OF FILE src/components/StyleChamber.tsx ---