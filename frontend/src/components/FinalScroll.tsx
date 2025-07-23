// --- START OF FILE src/components/FinalScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';

// A helper component for a card with a copy button.
const CopyCard = ({ title, content }: { title: string; content: string }) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    // We can add a visual confirmation later (e.g., "Copied!").
  };

  return (
    <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-serif text-xl font-bold text-saga-secondary">{title}</h3>
        <button 
          onClick={handleCopy}
          className="bg-saga-bg text-saga-primary px-3 py-1 rounded-md text-sm hover:bg-saga-primary hover:text-white transition-colors"
        >
          Copy
        </button>
      </div>
      <p className="text-saga-text-dark whitespace-pre-wrap font-sans">{content}</p>
    </div>
  );
};

// A helper component for a clickable action card.
const ActionCard = ({ title, description, icon, onClick }: { title: string; description: string; icon: string; onClick: () => void; }) => {
  return (
    <button
      onClick={onClick}
      className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 text-left
                 hover:border-saga-primary hover:scale-105 transition-all duration-300"
    >
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="font-serif text-xl font-bold text-saga-secondary mb-2">{title}</h3>
      <p className="text-saga-text-dark">{description}</p>
    </button>
  );
};


/**
 * FinalScroll: Displays the final generated marketing asset with its associated actions.
 */
export default function FinalScroll() {
  const finalAsset = useMarketingStore((state) => state.finalAsset);
  const resetForge = useMarketingStore((state) => state.resetForge);

  if (!finalAsset) {
    return <div className="text-center p-8">The prophecy is faint... No asset was found.</div>;
  }

  // Placeholder functions for the action cards
  const handleGenerateImagePrompt = () => {
    console.log("Invoking ritual to generate image prompt details...");
    // Here we would trigger a new state/ritual for the image prompt display.
  };

  const handleGenerateVideoPrompt = () => {
    console.log("Invoking ritual to generate video prompt details...");
    // Here we would trigger a new state/ritual for the video prompt display.
  };

  return (
    <motion.div
      key="final-scroll"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Prophecy is Inscribed
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Wield these words of power as you see fit.
        </p>
      </header>

      <div className="space-y-8">
        {/* Card 1: The Main Content (Not Clickable) */}
        {/* We check if 'post_text' or 'body_copy' exists to handle different asset types */}
        {finalAsset.post_text && <CopyCard title={finalAsset.post_text.title} content={finalAsset.post_text.content} />}
        {finalAsset.body_copy && <CopyCard title={finalAsset.body_copy.title} content={finalAsset.body_copy.content} />}
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Card 2: Generate Image Prompt (Clickable) */}
          {finalAsset.image_prompt && (
            <ActionCard 
              title="Generate Image Prompt"
              description="Invoke a ritual to receive a detailed prompt for AI image generators and instructions on its use."
              icon="🖼️"
              onClick={handleGenerateImagePrompt}
            />
          )}

          {/* Card 3: Generate Video Prompt (Clickable) */}
          {finalAsset.video_prompt && (
            <ActionCard 
              title="Generate Video Prompt"
              description="Invoke a ritual to receive a detailed prompt for AI video generators and instructions on its use."
              icon="🎬"
              onClick={handleGenerateVideoPrompt}
            />
          )}
        </div>
      </div>

      {/* Reset Button to start a new prophecy in the forge */}
      <div className="text-center mt-16">
        <button 
          onClick={resetForge}
          className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors"
        >
          ← Return to the Anvil
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/FinalScroll.tsx ---