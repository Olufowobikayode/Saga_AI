// --- START OF REFACTORED FILE frontend/src/components/WeaversCrossroads.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useContentStore } from '@/store/contentStore';
import { useSession } from '@/hooks/useSession'; // <-- 1. IMPORT HOOK

// SAGA UI: Defining the data for our three core content type cards.
const contentTypes = [
  {
    id: 'Social Post',
    title: "Weave a Social Post",
    description: "Forge a platform-specific post, complete with visual prompts, to engage your audience.",
    icon: "📣"
  },
  {
    id: 'Comment',
    title: "Weave a Comment",
    description: "Craft an insightful, value-driven comment to build authority in online discussions.",
    icon: "💬"
  },
  {
    id: 'Blog Post',
    title: "Weave a Blog Post",
    description: "Inscribe a full, SEO-optimized scroll to establish yourself as a master of the topic.",
    icon: "✍️"
  }
];

/**
 * WeaversCrossroads: Displays the three main content type choices after a user
 * has selected a Content Spark.
 */
export default function WeaversCrossroads() {
  const { chooseContentType, chosenSpark } = useContentStore();

  // --- 2. USE SESSION HOOK ---
  const { sessionId, isLoading: isSessionLoading } = useSession();

  const handleContentTypeSelection = (type: 'Social Post' | 'Comment' | 'Blog Post') => {
    if (type === 'Blog Post') {
      // Blog posts trigger an API call immediately, so we need the session ID.
      if (isSessionLoading || !sessionId) {
        alert("Session is not yet ready. Please wait a moment.");
        return;
      }
    }
    // --- 3. PASS SESSION ID TO STORE ACTION ---
    // The store action will handle the logic of when to use the sessionId.
    chooseContentType(type, sessionId || '');
  };

  if (!chosenSpark) {
    return <div className="text-center p-8">The chosen spark has faded. Please return and select a thread of inspiration.</div>;
  }

  return (
    <motion.div
      key="weavers-crossroads"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Crossroads of Creation
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark max-w-2xl mx-auto">
          You have chosen the spark: "<span className="text-saga-secondary">{chosenSpark.title}</span>".
          <br />
          Now, declare the form this saga shall take.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {contentTypes.map((type, index) => (
          <motion.div
            key={type.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
          >
            <button
              onClick={() => handleContentTypeSelection(type.id as any)}
              disabled={isSessionLoading}
              className="w-full h-full bg-saga-surface p-8 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="text-5xl mb-4">{type.icon}</div>
              <h3 className="font-serif text-2xl font-bold text-saga-primary mb-2 group-hover:text-saga-secondary transition-colors">
                {type.title}
              </h3>
              <p className="text-saga-text-dark leading-relaxed">
                {type.description}
              </p>
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
// --- END OF REFACTORED FILE frontend/src/components/WeaversCrossroads.tsx ---