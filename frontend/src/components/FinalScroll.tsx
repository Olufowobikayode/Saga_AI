// --- START OF FILE src/components/FinalScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';
import SagaButton from './SagaButton'; // We need the button for the instructions card.

// --- Helper Components ---
const InfoCard = ({ title, content }: { title: string; content: string | object }) => {
    // This component remains the same.
    const renderContent = () => {
        if (typeof content === 'string') { return <p className="text-saga-text-dark whitespace-pre-wrap font-sans">{content}</p>; }
        if (typeof content === 'object' && content !== null) {
            return (
                <ul className="space-y-2">
                {Object.entries(content).map(([key, value]) => (
                    <li key={key} className="text-saga-text-dark">
                    <strong className="text-saga-text-light font-semibold">{key}: </strong> 
                    {Array.isArray(value) ? value.join(', ') : value}
                    </li>
                ))}
                </ul>
            );
        }
        return null;
    };
    return (
        <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
        <h3 className="font-serif text-xl font-bold text-saga-secondary mb-4">{title}</h3>
        {renderContent()}
        </div>
    );
};
const CopyCard = ({ title, content }: { title: string; content: string }) => {
    // This component remains the same.
    const handleCopy = () => { navigator.clipboard.writeText(content); };
    return (
        <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
        <div className="flex justify-between items-center mb-4">
            <h3 className="font-serif text-xl font-bold text-saga-secondary">{title}</h3>
            <button onClick={handleCopy} className="bg-saga-bg text-saga-primary px-3 py-1 rounded-md text-sm hover:bg-saga-primary hover:text-white transition-colors">Copy</button>
        </div>
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
    // This component remains the same.
    return (
        <button onClick={onClick} className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 text-left hover:border-saga-primary hover:scale-105 transition-all duration-300">
        <div className="text-4xl mb-4">{icon}</div>
        <h3 className="font-serif text-xl font-bold text-saga-secondary mb-2">{title}</h3>
        <p className="text-saga-text-dark">{description}</p>
        </button>
    );
};

// NEW: A dedicated card for hosting instructions.
const InstructionsCard = () => {
    return (
        <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
            <h3 className="font-serif text-xl font-bold text-saga-secondary mb-4">How to Host Your Page for Free</h3>
            <div className="space-y-4 text-saga-text-dark">
                <p>You can publish this page on the internet in seconds using a free service. Netlify Drop is the easiest path:</p>
                <ol className="list-decimal list-inside space-y-2">
                    <li>Copy the HTML code from the card above.</li>
                    <li>Paste it into a new text file on your computer and save it as <code className="bg-saga-bg text-saga-primary px-1 rounded">index.html</code>.</li>
                    <li>Click the button below to open Netlify Drop in a new tab.</li>
                    <li>Drag and drop your <code className="bg-saga-bg text-saga-primary px-1 rounded">index.html</code> file into the Netlify window.</li>
                </ol>
                <p>Your page will be live on the web instantly.</p>
            </div>
            <div className="mt-6">
                <SagaButton onClick={() => window.open('https://app.netlify.com/drop', '_blank')}>
                    Go to Netlify Drop
                </SagaButton>
            </div>
        </div>
    );
};

export default function FinalScroll() {
  const { finalAsset, chosenAssetType, resetForge, unveilPrompt } = useMarketingStore();

  if (!finalAsset) {
    return <div className="text-center p-8">The prophecy is faint... No asset was found.</div>;
  }

  const renderHtmlAsset = () => (
    <div className="space-y-8">
      {/* Card 1: The HTML Code */}
      {finalAsset.html_code && <CopyCard title={finalAsset.html_code.title} content={finalAsset.html_code.content} />}
      
      {/* Card 2: The Hosting Instructions */}
      <InstructionsCard />
      
      {/* Clickable cards for each image prompt */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {finalAsset.image_prompts && finalAsset.image_prompts.map((prompt: any, index: number) => (
          <ActionCard key={index} title={`Generate ${prompt.section}`} description={`Invoke a ritual to receive the prompt for the ${prompt.section.toLowerCase()}.`} icon="🖼️" onClick={() => unveilPrompt('Image')} />
        ))}
      </div>
    </div>
  );
  
  // --- The rest of the render functions remain the same ---
  const renderTextAsset = () => (
    <div className="space-y-8">
      {finalAsset.copy && <CopyCard title={finalAsset.copy.title} content={finalAsset.copy.content} />}
      {finalAsset.audience_rune && <InfoCard title={finalAsset.audience_rune.title} content={finalAsset.audience_rune.content} />}
      {finalAsset.platform_sigils && <InfoCard title={finalAsset.platform_sigils.title} content={finalAsset.platform_sigils.content} />}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {finalAsset.image_orb && <ActionCard title={finalAsset.image_orb.title} description={finalAsset.image_orb.description} icon="🖼️" onClick={() => unveilPrompt('Image')} />}
        {finalAsset.motion_orb && <ActionCard title={finalAsset.motion_orb.title} description={finalAsset.motion_orb.description} icon="🎬" onClick={() => unveilPrompt('Video')} />}
      </div>
    </div>
  );
  const renderReviewAsset = () => (
    <div className="space-y-8">
      {finalAsset.reviews && finalAsset.reviews.map((review: any, index: number) => (
        <CopyCard key={index} title={`Review Option ${index + 1}`} content={review.content} />
      ))}
    </div>
  );
  const renderAsset = () => {
    switch (chosenAssetType) {
      case 'Funnel Page':
      case 'Landing Page':
        return renderHtmlAsset();
      case 'Affiliate Review':
        return renderReviewAsset();
      default:
        return renderTextAsset();
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