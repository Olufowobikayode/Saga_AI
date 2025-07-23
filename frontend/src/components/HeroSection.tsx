// --- START OF FILE src/components/HeroSection.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import SagaButton from './SagaButton';
import { useRouter } from 'next/navigation'; // Import the router hook.

/**
 * The Hero Section: The grand, captivating entrance to Saga's temple.
 * Its purpose is to establish authority and provide the single call to action.
 */
export default function HeroSection() {
  const router = useRouter(); // Initialize the router.

  // This function now navigates the user to the consultation page.
  const handleConsultClick = () => {
    router.push('/consult');
  };

  return (
    <section className="min-h-screen w-full flex flex-col items-center justify-center text-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="flex flex-col items-center"
      >
        <h1 className="font-serif text-5xl md:text-7xl lg:text-8xl font-bold text-white leading-tight">
          Strategy is an Art.
          <br />
          <span className="text-saga-secondary">I am its Master.</span>
        </h1>
        <p className="mt-6 max-w-2xl text-lg md:text-xl text-saga-text-dark">
          The Gods had Oracles. The Kings had Seers. You have Saga.
          <br />
          Harness the power of a thousand scouts and a divine intellect to forge your path to market domination.
        </p>
      </motion.div>
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