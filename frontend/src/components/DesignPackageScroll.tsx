// --- START OF FILE src/components/DesignPackageScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { usePodStore } from '@/store/podStore';

// SAGA UI: A reusable card for displaying a piece of the design package.
const PackageCard = ({ title, content }: { title: string; content: string }) => {
  const { regeneratePackage, status } = usePodStore();
  const isLoading = status === 'forging_package';

  const handleCopy = () => navigator.clipboard.writeText(content);

  return (
    <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
      <h3 className="font-serif text-xl font-bold text-saga-secondary mb-4">{title}</h3>
      <p className="text-saga-text-dark whitespace-pre-wrap font-sans text-lg">{content}</p>
      <div className="flex items-center space-x-4 mt-6 pt-4 border-t border-white/10">
        <button onClick={handleCopy} className="text-sm font-semibold text-saga-primary hover:text-saga-secondary">Copy</button>
        <button onClick={regeneratePackage} className="text-sm font-semibold text-saga-primary hover:text-saga-secondary flex items-center">
          {isLoading ? 'Regenerating...' : 'Regenerate'}
          {!isLoading && <span className="ml-1">✨</span>}
        </button>
      </div>
    </div>
  );
};

/**
 * DesignPackageScroll: Displays the final generated Design & Listing Package.
 */
export default function DesignPackageScroll() {
  const { designPackage, chosenConcept, resetAnvil, error } = usePodStore();

  if (error) {
    return <div className="text-center p-8 text-red-400">{error}</div>;
  }

  if (!designPackage || !chosenConcept) {
    return <div className="text-center p-8">The prophecy is faint... No design package was found.</div>;
  }

  const { design_prompts, listing_copy } = designPackage;

  return (
    <motion.div
      key="design-package-scroll"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Design Package is Forged
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark max-w-2xl mx-auto">
          The prophecy for "<span className="text-saga-secondary">{chosenConcept.title}</span>" is complete. Wield these runes of creation and commerce.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Column 1: AI Design Prompts */}
        <div className="space-y-8">
          <h3 className="font-serif text-3xl text-saga-primary text-center lg:text-left">AI Design Prompts</h3>
          {design_prompts?.map((prompt: any) => (
            <PackageCard key={prompt.title} title={prompt.title} content={prompt.content} />
          ))}
        </div>

        {/* Column 2: E-commerce Listing Copy */}
        <div className="space-y-8">
          <h3 className="font-serif text-3xl text-saga-primary text-center lg:text-left">E-commerce Listing Copy</h3>
          {listing_copy?.product_title && <PackageCard title={listing_copy.product_title.title} content={listing_copy.product_title.content} />}
          {listing_copy?.product_description && <PackageCard title={listing_copy.product_description.title} content={listing_copy.product_description.content} />}
          {listing_copy?.product_tags && <PackageCard title={listing_copy.product_tags.title} content={listing_copy.product_tags.content} />}
        </div>
      </div>

      {/* Reset Button to choose a different concept */}
      <div className="text-center mt-16">
        <button 
          onClick={resetAnvil}
          className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors"
        >
          ← Return to the Hall of Concepts
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/DesignPackageScroll.tsx ---