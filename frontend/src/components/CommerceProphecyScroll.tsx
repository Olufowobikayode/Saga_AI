// --- START OF FILE src/components/CommerceProphecyScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useCommerceStore } from '@/store/commerceStore';

// SAGA UI: A recursive component to beautifully render any JSON-like object from the prophecy.
const ProphecyDetailRenderer = ({ data, title }: { data: any, title?: string }) => {
    if (!data || typeof data !== 'object') return null;

    // Filter out internal keys that are handled elsewhere.
    const keysToRender = Object.keys(data).filter(key => !['audit_type', 'prophecy_mode', 'title'].includes(key));

    return (
        <div className="bg-saga-bg p-4 rounded-lg border border-saga-surface mt-4">
            {title && <h3 className="font-serif text-xl text-saga-primary mb-4 border-b border-saga-primary/20 pb-2">{title}</h3>}
            <div className="space-y-4">
                {keysToRender.map(key => {
                    const value = data[key];
                    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                        return <ProphecyDetailRenderer key={key} data={value} title={formattedKey} />;
                    }
                     if (Array.isArray(value) && value.every(item => typeof item === 'object')) {
                        return (
                            <div key={key}>
                                <strong className="block text-saga-text-light font-semibold text-lg">{formattedKey}:</strong>
                                <div className="space-y-3 mt-2 pl-4 border-l-2 border-saga-surface">
                                    {value.map((item, index) => <ProphecyDetailRenderer key={index} data={item} />)}
                                </div>
                            </div>
                        );
                    }
                    return (
                        <div key={key}>
                            <strong className="block text-saga-text-light font-semibold">{formattedKey}:</strong>
                            <p className="text-saga-text-dark whitespace-pre-wrap pl-2">{Array.isArray(value) ? value.join(', ') : String(value)}</p>
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
  
  // Use the title from within the prophecy if it exists, otherwise use the chosen type.
  const prophecyTitle = finalProphecy.title || chosenProphecyType;

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
          The prophecy for your <span className="text-saga-secondary">{prophecyTitle}</span> is revealed.
        </p>
      </header>

      <div className="bg-saga-surface p-6 md:p-8 rounded-lg border border-white/10 shadow-lg">
        <ProphecyDetailRenderer data={finalProphecy} />
        
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