'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';
import InputRune from './InputRune';
import SagaButton from './SagaButton';

/**
 * QueryForm: The first stage of the Grand Ritual. Captures the user's
 * core query and desired tone.
 */
export default function QueryForm() {
  const submitQuery = useSagaStore((state) => state.submitQuery);
  // CORRECTED: Check for the new, unified 'forging' state.
  // The old check was for a state like 'performing_rite_1' which no longer exists.
  const isLoading = useSagaStore((state) => state.status === 'forging');

  const [interest, setInterest] = useState('');
  const [subNiche, setSubNiche] = useState('');
  const [toneText, setToneText] = useState('');
  const [toneUrl, setToneUrl] = useState('');

  const handleSubmit = () => {
    if (!interest) {
      alert("The Oracle requires an Interest or Niche to begin the ritual.");
      return;
    }
    // SAGA LOGIC: Call the rite from the store with the collected data.
    // This will trigger the first ritual and advance the state.
    submitQuery(interest, subNiche, toneText, toneUrl);
  };

  return (
    <motion.div
      key="query-form"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
          The Altar of Inquiry
        </h1>
        <p className="mt-4 text-xl text-saga-text-dark">
          Step 1 of 3: Present your core query.
        </p>
      </header>

      <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} 
          className="space-y-8"
        >
          <InputRune
            id="interest"
            label="Interest or Niche"
            placeholder="e.g., 'sustainable home goods', 'AI-powered productivity'"
            value={interest}
            onChange={(e) => setInterest(e.target.value)}
          />

          <InputRune
            id="subNiche"
            label="Sub-Niche or Specific Topic"
            placeholder="e.g., 'for small apartments', 'for busy professionals'"
            value={subNiche}
            onChange={(e) => setSubNiche(e.target.value)}
            optional
          />

          <div className="border-t border-saga-primary/20 pt-8">
            <p className="text-center text-saga-text-dark mb-4">
              To adopt your voice, provide either a sample of your writing OR a link to it.
            </p>
            <InputRune
              id="toneText"
              label="Your Writing Style"
              as="textarea"
              placeholder="Paste a sample of your writing..."
              value={toneText}
              onChange={(e) => setToneText(e.target.value)}
              optional
            />
            <p className="text-center my-4 font-serif text-saga-text-dark">OR</p>
            <InputRune
              id="toneUrl"
              label="Link to Your Writing"
              type="url"
              placeholder="https://your-blog.com/about-me"
              value={toneUrl}
              onChange={(e) => setToneUrl(e.target.value)}
              optional
            />
          </div>

          <div className="pt-4 text-center">
            <SagaButton onClick={handleSubmit} className="py-3 px-8 text-lg" disabled={isLoading}>
              {isLoading ? "Observing Ritual..." : "Next: Declare Artifact"}
            </SagaButton>
          </div>
        </form>
      </div>
    </motion.div>
  );
}