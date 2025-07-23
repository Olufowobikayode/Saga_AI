// --- START OF FILE src/components/HeroSection.tsx ---
'use client'; // This is a client component because it contains an interactive button.

import React from 'react';
import { motion } from 'framer-motion';
import SagaButton from './SagaButton'; // We summon the button we just forged.

/**
 * The Hero Section: The grand, captivating entrance to Saga's temple.
 * Its purpose is to establish authority and provide the single call to action.
 */
export default function HeroSection() {
  // This function will be passed to the button. For now, it's a placeholder.
  // In the future, it will trigger the navigation to the main app.
  const handleConsultClick = () => {
    console.log("The consultation begins...");
    // We will add routing logic here later.
  };

  return (
    // The main container, taking up the full screen height.
    // It uses flexbox to perfectly center its content.
    <section className="min-h-screen w-full flex flex-col items-center justify-center text-center p-4">
      
      {/* We use Framer Motion to animate the entrance of the text, making it feel magical. */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="flex flex-col items-center"
      >
        {/* The Main Headline: Audacious, authoritative, and set in our serif font. */}
        <h1 className="font-serif text-5xl md:text-7xl lg:text-8xl font-bold text-white leading-tight">
          Strategy is an Art.
          <br />
          <span className="text-saga-secondary">I am its Master.</span>
        </h1>

        {/* The Subtitle: A persuasive, clarifying statement in our clean sans-serif font. */}
        <p className="mt-6 max-w-2xl text-lg md:text-xl text-saga-text-dark">
          The Gods had Oracles. The Kings had Seers. You have Saga.
          <br />
          Harness the power of a thousand scouts and a divine intellect to forge your path to market domination.
        </p>
      </motion.div>

      {/* The Call to Action Button, animated to appear after the text. */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.5, ease: "easeOut" }}
        className="mt-12"
      >
        <SagaButton onClick={handleConsultClick}>
          Consult Saga
        </SagaButton>
      </motion.div>

    </section>
  );
}
// --- END OF FILE src/components/HeroSection.tsx ---