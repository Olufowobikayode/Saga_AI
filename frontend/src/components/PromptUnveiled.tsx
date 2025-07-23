// --- START OF FILE src/components/PromptUnveiled.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import SagaButton from './SagaButton';

// A helper component for the copyable prompt card.
const PromptCard = ({ title, content }: { title: string; content: string }) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(content);
  };

  return (
    <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-serif text-xl font-bold text-saga-secondary">{title}</h3>
        <button 
          onClick={handleCopy}
          className="bg-saga-bg text-saga-primary px-3 py-1 rounded-md text-sm hover:bg-saga-primary hover:text-white transition-colors"
        >
          Copy Prompt
        </button>
      </div>
      <p className="text-saga-text-dark whitespace-pre-wrap font-sans text-lg">{content}</p>
    </div>
  );
};

// SAGA LOGIC: Defining the properties for this component.
interface PromptUnveiledProps {
  promptType: 'Image' | 'Video';
  promptTitle: string;
  promptContent: string;
  platformName: string;
  platformUrl: string;
  instructions: string;
  onBack: () => void; // A function to return to the previous screen.
}

/**
 * PromptUnveiled: Displays a generated AI prompt and instructions for its use.
 */
export default function PromptUnveiled({
  promptType,
  promptTitle,
  promptContent,
  platformName,
  platformUrl,
  instructions,
  onBack,
}: PromptUnveiledProps) {

  const handlePlatformClick = () => {
    window.open(platformUrl, '_blank');
  };

  return (
    <motion.div
      key="prompt-unveiled"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The {promptType} Prompt is Unveiled
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Use this incantation to summon your vision.
        </p>
      </header>

      <div className="space-y-8">
        {/* Card 1: The Prompt Itself */}
        <PromptCard title={promptTitle} content={promptContent} />

        {/* Card 2: Instructions and Link */}
        <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
          <h3 className="font-serif text-xl font-bold text-saga-secondary mb-4">
            How to Use This Rune
          </h3>
          <p className="text-saga-text-dark mb-6">{instructions}</p>
          <SagaButton onClick={handlePlatformClick}>
            Go to {platformName}
          </SagaButton>
        </div>
      </div>

      {/* Back Button to return to the Final Scroll */}
      <div className="text-center mt-16">
        <button 
          onClick={onBack}
          className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors"
        >
          ← Return to the Final Scroll
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/PromptUnveiled.tsx ---