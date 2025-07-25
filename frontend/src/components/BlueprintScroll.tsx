// --- START OF FILE src/components/BlueprintScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useVentureStore } from '@/store/ventureStore';

// SAGA UI: A reusable component for each section of the blueprint.
const BlueprintSection = ({ title, children }: { title: string, children: React.ReactNode }) => (
    <div className="bg-saga-bg p-6 rounded-lg border border-saga-surface">
        <h3 className="font-serif text-2xl text-saga-primary mb-4 border-b border-saga-primary/20 pb-2">{title}</h3>
        <div className="space-y-3 text-saga-text-dark leading-relaxed">
            {children}
        </div>
    </div>
);

/**
 * BlueprintScroll: Displays the final, detailed business blueprint prophecy.
 */
export default function BlueprintScroll() {
  const { blueprint, chosenVision, regenerateBlueprint, returnToVisions, status } = useVentureStore();
  const isLoading = status === 'forging_blueprint';

  if (!blueprint || !chosenVision) {
    return <div className="text-center p-8">The vision is unclear... The blueprint could not be forged.</div>;
  }

  return (
    <motion.div
      key="blueprint-scroll"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Blueprint for <span className="text-saga-secondary">{chosenVision.title}</span> is Forged
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          The path to this new reality is now clear. Follow these runes to victory.
        </p>
      </header>
      
      <div className="bg-saga-surface p-6 md:p-8 rounded-lg border border-white/10 shadow-lg space-y-6">
        <BlueprintSection title="Strategic Summary">
          <p>{blueprint.summary}</p>
        </BlueprintSection>

        <BlueprintSection title="Target Audience Profile">
          <p>{blueprint.target_audience}</p>
        </BlueprintSection>

        <BlueprintSection title="Marketing Plan">
          <p><strong>Unique Selling Proposition:</strong> {blueprint.marketing_plan?.unique_selling_proposition}</p>
          <div>
            <strong>Content Pillars:</strong>
            <ul className="list-disc list-inside ml-4">
              {blueprint.marketing_plan?.content_pillars.map((pillar: string, index: number) => <li key={index}>{pillar}</li>)}
            </ul>
          </div>
           <div>
            <strong>Promotion Channels:</strong>
            <ul className="list-disc list-inside ml-4">
              {blueprint.marketing_plan?.promotion_channels.map((channel: string, index: number) => <li key={index}>{channel}</li>)}
            </ul>
          </div>
        </BlueprintSection>
        
        <BlueprintSection title="Sourcing & Operations">
          <p>{blueprint.sourcing_and_operations}</p>
        </BlueprintSection>
        
        <BlueprintSection title="First Three Runes of Action">
          <ol className="list-decimal list-inside space-y-2">
            {blueprint.first_three_steps.map((step: string, index: number) => <li key={index}>{step}</li>)}
          </ol>
        </BlueprintSection>
        
        {/* Actions Footer */}
        <div className="flex items-center space-x-6 pt-6 border-t border-white/10">
          <button 
            onClick={() => navigator.clipboard.writeText(JSON.stringify(blueprint, null, 2))}
            className="font-semibold text-saga-primary hover:text-saga-secondary transition-colors"
          >
            Copy Full Blueprint (JSON)
          </button>
          <button 
            onClick={regenerateBlueprint}
            className="font-semibold text-saga-primary hover:text-saga-secondary flex items-center transition-colors"
          >
            {isLoading ? "Regenerating..." : "Regenerate Blueprint"}
            {!isLoading && <span className="ml-1">✨</span>}
          </button>
        </div>
      </div>

      <div className="text-center mt-16">
        <button onClick={returnToVisions} className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors">
          ← Return to the Hall of Visions
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/BlueprintScroll.tsx ---