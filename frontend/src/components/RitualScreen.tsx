// --- START OF FILE src/components/RitualScreen.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// SAGA UI: A collection of wisdom to display during the ritual.
const wisdomQuotes = [
  "A strategy without data is merely a wish.",
  "The whispers of the market are the winds of fortune.",
  "Victory is forged in the fires of preparation.",
  "The wise ruler listens to the people, not the echoes of their own hall.",
  "Foresight is the art of seeing the inevitable before it occurs.",
  "Do not chase the trend. Understand the need that drives it."
];

// SAGA UI: The steps of the divination process.
const ritualSteps = [
  "Consulting the Seers of Community...",
  "Reading the Runes of Google Trends...",
  "Dispatching the Scout to Niche Realms...",
  "Deciphering the Chants of the Seekers...",
  "Weaving the Threads of Fate...",
  "Awaiting the Oracle's Prophecy..."
];

/**
 * RitualScreen: An immersive, full-screen overlay that displays the
 * divination process, fulfilling the 30-second ad requirement.
 */
export default function RitualScreen() {
  const [currentStep, setCurrentStep] = useState(0);
  const [currentQuote, setCurrentQuote] = useState(0);

  // SAGA LOGIC: This effect manages the animation of the ritual steps.
  useEffect(() => {
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => (prev < ritualSteps.length - 1 ? prev + 1 : prev));
    }, 4000); // Each step takes 4 seconds to "complete".

    return () => clearInterval(stepInterval);
  }, []);

  // SAGA LOGIC: This effect cycles through the wisdom quotes.
  useEffect(() => {
    const quoteInterval = setInterval(() => {
      setCurrentQuote(prev => (prev + 1) % wisdomQuotes.length);
    }, 5000); // A new quote appears every 5 seconds.

    return () => clearInterval(quoteInterval);
  }, []);

  return (
    <motion.div
      className="fixed inset-0 bg-saga-bg bg-cosmic-gradient z-50 flex flex-col items-center justify-center p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center">
        {/* Animated Wisdom Quote */}
        <AnimatePresence mode="wait">
          <motion.p
            key={currentQuote}
            className="font-serif text-2xl md:text-3xl text-saga-secondary mb-12 italic"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.8 }}
          >
            "{wisdomQuotes[currentQuote]}"
          </motion.p>
        </AnimatePresence>

        {/* The list of ritual steps */}
        <div className="space-y-4 max-w-md mx-auto">
          {ritualSteps.map((step, index) => (
            <motion.div
              key={step}
              className="flex items-center text-lg"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
            >
              {/* The checkmark / spinner */}
              <div className="w-8 h-8 mr-4 flex items-center justify-center">
                <AnimatePresence>
                  {index < currentStep ? (
                    // If the step is complete, show an animated checkmark.
                    <motion.svg
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-6 h-6 text-saga-primary"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </motion.svg>
                  ) : (
                    // If the step is in progress, show a spinning circle.
                    <motion.div
                      className="w-5 h-5 border-2 border-saga-text-dark border-t-saga-primary rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    />
                  )}
                </AnimatePresence>
              </div>
              <span className={index <= currentStep ? "text-saga-text-light" : "text-saga-text-dark"}>
                {step}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/RitualScreen.tsx ---