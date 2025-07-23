// --- START OF FILE src/components/FeaturesSection.tsx ---
'use client'; // This component uses Framer Motion for animations, so it's a client component.

import React from 'react';
import { motion } from 'framer-motion';

// SAGA UI: Defining the structure for each feature we will display.
const features = [
  {
    title: "The All-Seeing Eye",
    description: "Saga does not guess. She dispatches a thousand digital seers to scour the live market—analyzing trends, deciphering community whispers, and identifying your rivals' weaknesses in real-time.",
    icon: "👁️" // Using emojis as simple, powerful icons.
  },
  {
    title: "The Weaver's Loom",
    description: "Raw data is chaos. Saga is the master weaver, taking disparate threads of intelligence and forging them into a single, coherent tapestry of strategy. Every prophecy is a synthesis of all available knowledge.",
    icon: "🕸️"
  },
  {
    title: "The Runes of Action",
    description: "Wisdom without action is worthless. Every prophecy concludes with a clear, actionable battle plan. Saga does not offer suggestions; she provides commands for you to execute on your path to victory.",
    icon: "📜"
  }
];

/**
 * The Features Section: The "Scroll of Power" that explains Saga's core capabilities.
 * It appears as the user scrolls down from the Hero section.
 */
export default function FeaturesSection() {
  return (
    // The main container for this section with vertical padding.
    <section className="py-20 px-4 w-full">
      <div className="max-w-5xl mx-auto">
        
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.5 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
            The Three Pillars of Prophecy
          </h2>
          <p className="mt-4 text-lg text-saga-text-dark">
            My wisdom is not born of ether, but forged in the fires of data.
          </p>
        </motion.div>

        {/* Grid container for the feature cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              // Each card will animate into view as the user scrolls.
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.5 }}
              transition={{ duration: 0.5, delay: index * 0.2 }} // Staggered animation delay.
              
              // SAGA UI: The styling for each "ProphecyCard".
              className="bg-saga-surface p-8 rounded-lg border border-white/10 shadow-lg"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="font-serif text-2xl font-bold text-saga-secondary mb-3">
                {feature.title}
              </h3>
              <p className="text-saga-text-dark leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
// --- END OF FILE src/components/FeaturesSection.tsx ---