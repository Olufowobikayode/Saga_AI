// --- START OF REFACTORED FILE frontend/src/components/SparkForm.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useContentStore } from '@/store/contentStore';
import { useSession } from '@/hooks/useSession'; // <-- 1. IMPORT HOOK
import InputRune from './InputRune';
import SagaButton from './SagaButton';

/**
 * SparkForm: The component where a user inputs or confirms the topic
 * for which Saga will generate "Content Sparks".
 */
export default function SparkForm() {
  const { tacticalInterest, generateSparks, status } = useContentStore();
  const isLoading = status === 'weaving_sparks';

  // --- 2. USE THE SESSION HOOK ---
  const { sessionId, isLoading: isSessionLoading } = useSession();

  // Local state for the form input.
  const [topic, setTopic] = useState('');

  useEffect(() => {
    if (tacticalInterest) {
      setTopic(tacticalInterest);
    }
  }, [tacticalInterest]);

  const handleSubmit = () => {
    if (!topic) {
      alert("The Weaver requires a topic to find the threads of inspiration.");
      return;
    }
    if (isSessionLoading || !sessionId) {
      alert("Session is not yet ready. Please wait a moment.");
      return;
    }
    // SAGA LOGIC: The store now handles the topic, just pass the session ID.
    // --- 3. PASS THE SESSION ID TO THE STORE ACTION ---
    generateSparks(sessionId);
  };

  return (
    <motion.div
      key="spark-form"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
        <header className="text-center border-b border-saga-primary/20 pb-6 mb-8">
          <h2 className="font-serif text-3xl text-saga-primary">The Seed of Wisdom</h2>
          <p className="text-saga-text-dark mt-2">
            Confirm or refine the topic for which Saga shall divine content ideas.
          </p>
        </header>

        <form 
          onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} 
          className="space-y-8"
        >
          <InputRune
            id="topic"
            label="Content Topic"
            placeholder="Enter the core topic for your content..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />

          <div className="pt-4 text-center">
            <SagaButton 
              onClick={handleSubmit} 
              className="py-3 px-8 text-lg"
              disabled={isLoading || isSessionLoading}
            >
              {isSessionLoading ? "Awaiting Session..." : (isLoading ? "Observing Ritual..." : "Generate Content Sparks")}
            </SagaButton>
          </div>
        </form>
      </div>
    </motion.div>
  );
}
// --- END OF REFACTORED FILE frontend/src/components/SparkForm.tsx ---