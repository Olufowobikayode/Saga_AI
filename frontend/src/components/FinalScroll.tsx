// --- START OF FILE src/components/FinalScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';
import SagaButton from './SagaButton';

// --- Helper Components ---

// UPDATED: This component now intelligently renders strings OR structured objects.
const InfoCard = ({ title, content }: { title: string; content: string | { [key: string]: any } }) => {
  const renderContent = () => {
    if (typeof content === 'string') {
      return <p className="text-saga-text-dark whitespace-pre-wrap font-sans">{content}</p>;
    }
    // Handle the structured object for Audience Rune and Platform Sigils
    if (typeof content === 'object' && content !== null) {
      return (
        <ul className="space-y-3">
          {Object.entries(content).map(([key, value]) => (
            <li key={key} className="text-saga-text-dark leading-relaxed">
              <strong className="block text-saga-text-light font-semibold">{key.replace(/_/g, ' ')}:</strong> 
              <span>{Array.isArray(value) ? value.join(', ') : String(value)}</span>
            </li>
          ))}
        </ul>
      );
    }
    return null;
  };

  return (
    <div className="bg-saga-surface p-6 rounded-lg border border-white/10 h-full">
      <h3 className="font-serif text-xl font-bold text-saga-secondary mb-4">{title}</h3>
      {renderContent()}
    </div>
  );
};

const CopyCard = ({ title, content }: { title: string; content: string }) => {
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
    return (
        <button onClick={onClick} className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 text-left hover:border-saga-primary hover:scale-105 transition-all duration-300">
        <div className="text-4xl mb-4">{icon}</div>
        <h3 className="font-serif text-xl font-bold text-saga-secondary mb-2">{title}</h3>
        <p className="text-saga-text-dark">{description}</p>
        </button>
    );
};

const InstructionsCard = () => { /* ... same as before ... */ };


export default function FinalScroll() {
  const { finalAsset, chosenAssetType, resetForge, unveilPrompt, unfurlScroll } = useMarketingStore();

  if (!finalAsset) {
    return <div className="text-center p-8">The prophecy is faint... No asset was found.</div>;
  }

  // REFACTORED: This now renders the full 5-card "Campaign Deployment Kit".
  const renderTextAsset = () => (
    <div className="space-y-8">
      {/* Card 1: The Scroll (Copy) - Not Clickable */}
      {finalAsset.copy && <CopyCard title={finalAsset.copy.title} content={finalAsset.copy.content} />}
      
      {/* Grid for the info cards to sit side-by-side on larger screens */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Card 2: The Audience Rune (Targeting) - Not Clickable */}
        {finalAsset.audience_rune && <InfoCard title={finalAsset.audience_rune.title} content={finalAsset.audience_rune.content} />}
        
        {/* Card 3: The Scribe's Sigils (Platform Setup) - Not Clickable */}
        {finalAsset.platform_sigils && <InfoCard title={finalAsset.platform_sigils.title} content={finalAsset.platform_sigils.content} />}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Card 4: The Image Orb - Clickable */}
        {finalAsset.image_orb && (
          <ActionCard 
            title={finalAsset.image_orb.title}
            description={finalAsset.image_orb.description}
            icon="🖼️"
            onClick={() => unveilPrompt('Image')}
          />
        )}

        {/* Card 5: The Motion Orb - Clickable */}
        {finalAsset.motion_orb && (
          <ActionCard 
            title={finalAsset.motion_orb.title}
            description={finalAsset.motion_orb.description}
            icon="🎬"
            onClick={() => unveilPrompt('Video')}
          />
        )}
      </div>
    </div>
  );
  
  // REFACTORED: This now renders the clickable ActionCards for HTML assets.
  const renderHtmlAsset = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {/* Card 1: View HTML Code - Clickable */}
        <ActionCard title="View HTML Code" description="Unfurl the scroll containing the complete, SEO-optimized HTML for your page." icon="📜" onClick={() => unfurlScroll('html_code')} />
        
        {/* Card 2: View Deployment Guide - Clickable */}
        <ActionCard title="View Deployment Guide" description="Unfurl the scroll with custom, step-by-step instructions for deploying and ranking your page." icon="🗺️" onClick={() => unfurlScroll('deployment_guide')} />

        {/* Card 3+: Generate Visuals - Clickable */}
        {finalAsset.image_prompts && finalAsset.image_prompts.map((prompt: any, index: number) => (
          <ActionCard key={index} title={`Generate ${prompt.section}`} description={`Invoke a ritual for the ${prompt.section.toLowerCase()} prompt.`} icon="🖼️" onClick={() => unveilPrompt('Image')} />
        ))}
    </div>
  );

  // This render function remains the same.
  const renderReviewAsset = () => ( /* ... */ );
  
  const renderAsset = () => {
    switch (chosenAssetType) {
      case 'Funnel Page':
      case 'Landing Page':
        return renderHtmlAsset();
      case 'Affiliate Review':
        return renderReviewAsset();
      default: // Ad Copy, Email Copy, Affiliate Copy
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
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Prophecy is Inscribed
        </h2>
        {/* The subtitle changes based on the asset type for a more dynamic feel */}
        {chosenAssetType === 'Funnel Page' || chosenAssetType === 'Landing Page' ?
          <p className="mt-4 text-lg text-saga-text-dark">The blueprints are forged. Unfurl the scrolls to reveal their secrets.</p>
          :
          <p className="mt-4 text-lg text-saga-text-dark">Wield these words of power as you see fit.</p>
        }
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