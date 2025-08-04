'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { usePodStore } from '@/store/podStore';
import { useSession } from '@/hooks/useSession'; // <-- 1. IMPORT HOOK

/**
 * HallOfConcepts: Displays the AI-generated "Design Concept" cards for the user to choose from.
 */
export default function HallOfConcepts() {
  // SAGA LOGIC: Get the generated concepts and the 'chooseConcept' function from the store.
  const { opportunitiesResult, chooseConcept, nicheInterest, chosenStyle, error } = usePodStore();

  // --- 2. USE SESSION HOOK ---
  const { sessionId, isLoading: isSessionLoading } = useSession();

  const handleChooseConcept = (conceptId: string) => {
    if (isSessionLoading || !sessionId) {
        alert("Session is not yet ready. Please wait a moment.");
        return;
    }
    // --- 3. PASS SESSION ID TO STORE ACTION ---
    chooseConcept(conceptId, sessionId);
  };

  if (error) {
    return <div className="text-center p-8 text-red-400">{error}</div>;
  }
  
  const concepts = opportunitiesResult?.design_concepts;

  if (!concepts || concepts.length === 0) {
    return <div className="text-center p-8">The forge is cold... Saga could not divine any concepts for this niche and style.</div>;
  }

  return (
    <motion.div
      key="hall-of-concepts"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Hall of Concepts
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark max-w-2xl mx-auto">
          Saga has foreseen several <span className="text-saga-secondary">{chosenStyle}</span> design opportunities within the niche of "<span className="text-saga-secondary">{nicheInterest}</span>".
          <br />
          Choose the concept you wish to forge into a final masterpiece.
        </p>
      </header>

      <div className="space-y-6">
        {concepts.map((concept, index) => (
          <motion.div
            key={concept.concept_id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <button
              onClick={() => handleChooseConcept(concept.concept_id)}
              disabled={isSessionLoading}
              className="w-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <h3 className="font-serif text-2xl font-bold text-saga-primary mb-2 group-hover:text-saga-secondary transition-colors">
                {concept.title}
              </h3>
              <p className="text-saga-text-light mb-3">
                {concept.description}
              </p>
              <p className="text-sm text-saga-text-dark mb-4 italic border-l-2 border-saga-primary/30 pl-3">
                Justification: {concept.justification}
              </p>
              <div className="flex flex-wrap gap-2">
                {concept.suggested_products.map(product => (
                  <span key={product} className="font-mono text-xs bg-saga-bg px-2 py-1 rounded-md text-saga-primary">
                    {product}
                  </span>
                ))}
              </div>
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
// --- END OF REFACTORED FILE frontend/src/components/HallOfConcepts.tsx ---