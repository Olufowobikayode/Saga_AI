// --- START OF FILE src/components/CommerceProphecyScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useCommerceStore } from '@/store/commerceStore';

// SAGA UI: A recursive component to beautifully render any JSON-like object.
const ProphecyDetailRenderer = ({ data, title }: { data: any, title?: string }) => {
    if (!data) return null;

    return (
        <div className="bg-saga-bg p-4 rounded-lg border border-saga-surface">
            {title && <h3 className="font-serif text-xl text-saga-primary mb-3">{title}</h3>}
            <div className="space-y-3">
                {Object.entries(data).map(([key, value]) => {
                    // Ignore internal keys like 'audit_type' or 'prophecy_mode' if we handle them elsewhere
                    if (['audit_type', 'prophecy_mode'].includes(key)) return null;

                    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                    if (typeof value === 'object' && value !== null) {
                        return <ProphecyDetailRenderer key={key} data={value} title={formattedKey} />;
                    }
                    return (
                        <div key={key}>
                            <strong className="block text-saga-text-light font-semibold">{formattedKey}:</strong>
                            <p className="text-saga-text-dark whitespace-pre-wrap">{Array.isArray(value) ? value.join(', ') : String(value)}</p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

/**
 * CommerceProphecyScroll: Displays the final, forged prophecy from the Commerce Saga.
 */
export default function CommerceProphecyScroll() {
  const { finalProphecy, chosenProphecyType, regenerateProphecy, returnToCrossroads, status } = useCommerceStore();
  const isLoading = status === 'forging_prophecy';

  if (!finalProphecy) {
    return <div className="text-center p-8">The prophecy is faint... No data was found.</div>;
  }
  
  return (
    <motion.div
      key="commerce-prophecy-scroll"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Ledger is Unfurled
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          The prophecy for your <span className="text-saga-secondary">{chosenProphecyType}</span> is revealed.
        </p>
      </header>

      <div className="bg-saga-surface p-6 md:p-8 rounded-lg border border-white/10 shadow-lg">
        <ProphecyDetailRenderer data={finalProphecy} />
        
        {/* Actions Footer */}
        <div className="flex items-center space-x-6 mt-6 pt-6 border-t border-white/10">
          <button 
            onClick={() => navigator.clipboard.writeText(JSON.stringify(finalProphecy, null, 2))}
            className="font-semibold text-saga-primary hover:text-saga-secondary transition-colors"
          >
            Copy Full Prophecy (JSON)
          </button>
          <button 
            onClick={regenerateProphecy}
            className="font-semibold text-saga-primary hover:text-saga-secondary flex items-center transition-colors"
          >
            {isLoading ? "Regenerating..." : "Regenerate"}
            {!isLoading && <span className="ml-1">✨</span>}
          </button>
        </div>
      </div>

      <div className="text-center mt-16">
        <button onClick={returnToCrossroads} className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors">
          ← Return to the Crossroads
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/CommerceProphecyScroll.tsx ---