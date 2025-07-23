// --- START OF FILE src/components/CTASection.tsx ---
'use client'; // This component contains an interactive button.

import React from 'react';
import { motion } from 'framer-motion';
import SagaButton from './SagaButton';

/**
 * The CTA Section: The final, powerful command to the user,
 * urging them to begin their journey with Saga.
 */
export default function CTASection() {
  // This function will be passed to the button.
  const handleConsultClick = () => {
    console.log("The final call to consultation has been answered...");
    // We will add routing logic here later.
  };

  return (
    // The main container for this section with significant vertical padding
    // and a subtle top border to separate it from the previous section.
    <section className="py-24 px-4 w-full border-t border-white/10 bg-black/20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.8 }}
        className="max-w-3xl mx-auto text-center"
      >
        {/* The Final Headline: A direct and powerful question. */}
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          Are You Ready to Command Your Market?
        </h2>

        {/* The Final Persuasive Text: Summarizes the value proposition. */}
        <p className="mt-6 text-lg md:text-xl text-saga-text-dark leading-relaxed">
          Uncertainty is the luxury of the common merchant. Victory demands foresight.
          The runes have been cast, the seers are waiting. All that is required is your command.
        </p>

        {/* The Final Button: A larger, more prominent version of our SagaButton. */}
        <div className="mt-12">
          <SagaButton 
            onClick={handleConsultClick}
            className="py-4 px-10 text-xl" // Making the button larger for emphasis.
          >
            Divine My Strategy
          </SagaButton>
        </div>
      </motion.div>
    </section>
  );
}
// --- END OF FILE src/components/CTASection.tsx ---