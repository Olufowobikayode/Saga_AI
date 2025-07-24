// --- START OF FILE src/components/RealmChamber.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useContentStore } from '@/store/contentStore';

// SAGA UI: Defining the data for our platform selection cards.
// This is a direct frontend representation of the backend's PLATFORM_NATURES dictionary.
const realmOptions = [
    { id: "Facebook", description: "Community-focused, conversational, supports text, images, and video.", icon: "👍" },
    { id: "YouTube", description: "Long-form video, educational content, vlogs, and tutorials.", icon: "📺" },
    { id: "Instagram", description: "Visually-driven, high-quality images and short videos (Reels).", icon: "📸" },
    { id: "TikTok", description: "Short-form, trend-driven, authentic video. Music and effects are key.", icon: "🎵" },
    { id: "X (formerly Twitter)", description: "Short, concise text updates, real-time conversation, and news-jacking.", icon: "🐦" },
    { id: "LinkedIn", description: "Professional, insightful articles and posts for career and business.", icon: "💼" },
    { id: "Pinterest", description: "High-quality vertical images (Pins) for inspiration and discovery.", icon: "📌" },
    { id: "Reddit", description: "Community-specific, authentic, text-heavy posts. Add value, don't self-promote.", icon: "👽" }
];

/**
 * RealmChamber: Allows the user to select the social media platform for their post.
 */
export default function RealmChamber() {
  // SAGA LOGIC: Get the necessary state and function from the store.
  const chooseRealm = useContentStore((state) => state.chooseRealm);
  const chosenTone = useContentStore((state) => state.chosenTone);

  return (
    <motion.div
      key="realm-chamber"
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
          In which digital realm shall this <span className="text-saga-secondary">{chosenTone}</span> saga be told?
        </p>
      </header>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {realmOptions.map((option, index) => (
          <motion.div
            key={option.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * index }}
          >
            <button
              onClick={() => chooseRealm(option.id)}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300 group"
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-serif text-2xl font-bold text-saga-primary group-hover:text-saga-secondary transition-colors">
                  {option.id}
                </h3>
                <div className="text-3xl">{option.icon}</div>
              </div>
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
// --- END OF FILE src/components/RealmChamber.tsx ---