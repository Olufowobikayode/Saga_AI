// --- START OF FILE src/components/FinalScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';

// --- Helper components remain the same ---
const CopyCard = ({ title, content }: { title: string; content: string }) => {
  const handleCopy = () => { navigator.clipboard.writeText(content); };
  return (
    <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-serif text-xl font-bold text-saga-secondary">{title}</h3>
        <button onClick={handleCopy} className="bg-saga-bg text-saga-primary px-3 py-1 rounded-md text-sm hover:bg-saga-primary hover:text-white transition-colors">Copy</button>
      </div>
      {/* Use a pre-formatted block for code, and paragraph for text */}
      {title.toLowerCase().includes('html') ? (
        <pre className="text-saga-text-dark whitespace-pre-wrap font-mono bg-saga-bg p-4 rounded-md text-sm overflow-x-auto">
          <code>{content}</code>
        </pre>
      ) : (
        <p className="text-saga-text-dark whitespace-pre-wrap font-sans">{content}</p>
      )}
    </div>
  );
};
const ActionCard = ({ title, description, icon, onClick }: { title: string; description: string; icon: string; onClick: () => void; }) => {
  return (
    <button onClick={onClick} className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 text-left hover:border-saga-primary hover:scale-105 transition-all duration-300">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="font-serif text-xl font-bold text-saga-secondary mb-2">{title}</h3>
      <p className="text-saga-text-dark">{description}</p>
    </button>
  );
};

export default function FinalScroll() {
  const { finalAsset, chosenAssetType, resetForge, unveilPrompt } = useMarketingStore();

  if (!finalAsset) {
    return <div className="text-center p-8">The prophecy is faint... No asset was found.</div>;
  }

  // SAGA LOGIC: This function determines which layout to render based on the asset type.
  const renderAsset = () => {
    switch (chosenAssetType) {
      case 'Funnel Page':
      case 'Landing Page':
        return (
          <div className="space-y-8">
            {/* Card 1: The HTML Code (Not Clickable) */}
            {finalAsset.html_code && <CopyCard title={finalAsset.html_code.title} content={finalAsset.html_code.content} />}
            
            {/* Clickable cards for each image prompt */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {finalAsset.image_prompts && finalAsset.image_prompts.map((prompt: any, index: number) => (
                <ActionCard
                  key={index}
                  title={`Generate ${prompt.section}`}
                  description={`Invoke a ritual to receive the prompt for the ${prompt.section.toLowerCase()}.`}
                  icon="🖼️"
                  onClick={() => {
                    // This is a simplified version. A real implementation might need to pass the specific prompt.
                    // For now, we'll just trigger the standard image prompt unveil.
                    unveilPrompt('Image');
                  }}
                />
              ))}
            </div>
          </div>
        );

      case 'Affiliate Review':
        // For reviews, we just display multiple copy cards.
        return (
          <div className="space-y-8">
            {finalAsset.reviews && finalAsset.reviews.map((review: any, index: number) => (
              <CopyCard key={index} title={`Review Option ${index + 1}`} content={review.content} />
            ))}
          </div>
        );

      // Default case for Ad Copy, Email Copy, Affiliate Copy
      default:
        return (
          <div className="space-y-8">
            {finalAsset.post_text && <CopyCard title={finalAsset.post_text.title} content={finalAsset.post_text.content} />}
            {finalAsset.body_copy && <CopyCard title={finalAsset.body_copy.title} content={finalAsset.body_copy.content} />}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {finalAsset.image_prompt && <ActionCard title="Generate Image Prompt" description="Invoke a ritual to receive a detailed prompt for AI image generators." icon="🖼️" onClick={() => unveilPrompt('Image')} />}
              {finalAsset.video_prompt && <ActionCard title="Generate Video Prompt" description="Invoke a ritual to receive a detailed prompt for AI video generators." icon="🎬" onClick={() => unveilPrompt('Video')} />}
            </div>
          </div>
        );
    }
  };

  return (
    <motion.div
      key="final-scroll"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">The Prophecy is Inscribed</h2>
        <p className="mt-4 text-lg text-saga-text-dark">Wield these words of power as you see fit.</p>
      </header>
      
      {renderAsset()}

      <div className="text-center mt-16">
        <button onClick={resetForge} className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors">
          ← Return to the Anvil
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/FinalScroll.tsx ---