// --- START OF FILE src/components/BlueprintScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useVentureStore } from '@/store/ventureStore';

// SAGA UI: A helper component for displaying a section of the blueprint.
const BlueprintSection = ({ title, children }: { title: string, children: React.ReactNode }) => (
  <section className="bg-saga-surface p-6 rounded-lg border border-white/10">
    <h3 className="font-serif text-2xl font-bold text-saga-primary mb-4 border-b border-saga-primary/20 pb-3">
      {title}
    </h3>
    <div className="space-y-4 text-saga-text-dark leading-relaxed">
      {children}
    </div>
  </section>
);

/**
 * BlueprintScroll: Displays the final, detailed business blueprint prophecy.
 */
export default function BlueprintScroll() {
  const { blueprint, regenerateBlueprint, resetSpire, status } = useVentureStore();
  const isLoading = status === 'forging_blueprint';

  if (!blueprint) {
    return <div className="text-center p-8">The blueprint is shrouded in mist... No plan was found.</div>;
  }

  // Helper to render nested objects cleanly
  const renderObjectList = (obj: object) => (
    <ul className="list-disc list-inside space-y-2">
      {Object.entries(obj).map(([key, value]) => (
        <li key={key}>
          <strong className="text-saga-text-light">{key.replace(/_/g, ' ')}:</strong> {value.calculation ? `${value.calculation} = $${value.value}` : String(value)}
        </li>
      ))}
    </ul>
  );

  return (
    <motion.div
      key="blueprint-scroll"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-saga-secondary">
          {blueprint.prophecy_title || "The Blueprint is Revealed"}
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark max-w-2xl mx-auto">
          {blueprint.summary || "Your path to this new venture is now clear. Follow this scroll to victory."}
        </p>
      </header>

      <div className="space-y-8">
        <BlueprintSection title="Target Audience">
          <p>{blueprint.target_audience}</p>
        </BlueprintSection>

        <BlueprintSection title="Marketing Plan">
          {blueprint.marketing_plan && renderObjectList(blueprint.marketing_plan)}
        </BlueprintSection>

        <BlueprintSection title="Sourcing & Operations">
          <p>{blueprint.sourcing_and_operations}</p>
        </BlueprintSection>
        
        <BlueprintSection title="Financial Omen (Worst Case, Month 1)">
          <p>{blueprint.worst_case_monthly_profit_omen?.scenario}</p>
          <div className="mt-4 border-t border-white/10 pt-4 space-y-2">
            {blueprint.worst_case_monthly_profit_omen?.estimated_revenue && <p><strong className="text-saga-text-light">Revenue:</strong> ${blueprint.worst_case_monthly_profit_omen.estimated_revenue.value}</p>}
            <div>
              <strong className="text-saga-text-light">Costs:</strong>
              <ul className="list-disc list-inside ml-4">
                {blueprint.worst_case_monthly_profit_omen?.estimated_costs?.map((cost: any, i: number) => <li key={i}>{cost.item}: ${cost.value}</li>)}
              </ul>
            </div>
            {blueprint.worst_case_monthly_profit_omen?.prophesied_profit && <p className="font-bold text-saga-primary"><strong className="text-saga-text-light">Prophesied Profit:</strong> ${blueprint.worst_case_monthly_profit_omen.prophesied_profit.value}</p>}
          </div>
          <p className="mt-4 italic text-sm">{blueprint.worst_case_monthly_profit_omen?.counsel}</p>
        </BlueprintSection>

        <BlueprintSection title="First Three Runes of Action">
          <ol className="list-decimal list-inside space-y-2">
            {blueprint.first_three_steps?.map((step: string, i: number) => <li key={i}>{step}</li>)}
          </ol>
        </BlueprintSection>
      </div>

      {/* Actions: Regenerate and Reset */}
      <div className="flex items-center justify-center space-x-8 mt-16">
        <button 
          onClick={resetSpire}
          className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors"
        >
          ← Choose a Different Vision
        </button>
        <button
          onClick={regenerateBlueprint}
          className="bg-saga-primary text-white font-bold font-serif text-lg py-3 px-6 rounded-lg hover:brightness-110 transition-all flex items-center"
        >
           {isLoading ? 'Regenerating...' : 'Regenerate Blueprint'}
           {!isLoading && <span className="ml-2">✨</span>}
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/BlueprintScroll.tsx ---