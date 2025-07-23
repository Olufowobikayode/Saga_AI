// --- START OF FILE src/components/CTASection.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import SagaButton from './SagaButton';
import { useRouter } from 'next/navigation'; // Import the router hook.

/**
 * The CTA Section: The final, powerful command to the user,
 * urging them to begin their journey with Saga.
 */
export default function CTASection() {
  const router = useRouter(); // Initialize the router.

  // This function now navigates the user to the consultation page.
  const handleConsultClick = () => {
    router.push('/consult');
  };

  return (
    <section className="py-24 px-4 w-full border-t border-white/10 bg-black/20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.8 }}
        className="max-w-3xl mx-auto text-center"
      >
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          Are You Ready to Command Your Market?
        </h2>
        <p className="mt-6 text-lg md:text-xl text-saga-text-dark leading-relaxed">
          Uncertainty is the luxury of the common merchant. Victory demands foresight.
          The runes have been cast, the seers are waiting. All that is required is your command.
        </p>
        <div className="mt-12">
          <SagaButton 
            onClick={handleConsultClick}
            className="py-4 px-10 text-xl"
          >
            Divine My Strategy
          </SagaButton>
        </div>
      </motion.div>
    </section>
  );
}
// --- END OF FILE src/components/CTASection.tsx ---