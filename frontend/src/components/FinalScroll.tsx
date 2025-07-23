// --- START OF FILE src/components/FinalScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';

// --- Helper Components ---

// Updated to handle more complex, structured content for targeting info.
const InfoCard = ({ title, content }: { title: string; content: string | object }) => {
  const renderContent = () => {
    if (typeof content === 'string') {
      return <p className="text-saga-text-dark whitespace-pre-wrap font-sans">{content}</p>;
    }
    // Handle structured content for targeting info
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
  const handleCopy = () => { navigator.clipboard.writeText(content); };
  return (
    <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-serif text-xl font-bold text-saga-secondary">{title}</h3>
        <button onClick={handleCopy} className="bg-saga-bg text-saga-primary px-3 py-1 rounded-md text-sm hover:bg-saga-primary hover:text-white transition-colors">Copy</button>
      </div>
      <p className="text-saga-text-dark whitespace-pre-wrap font-sans">{content}</p>
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

  // SAGA LOGIC: This function now renders the new 5-card layout for text assets.
  const renderTextAsset = () => (
    <div className="space-y-8">
      {/* Card 1: The Scroll (Copy) - Not Clickable */}
      {finalAsset.copy && <CopyCard title={finalAsset.copy.title} content={finalAsset.copy.content} />}
      
      {/* Card 2: The Audience Rune (Targeting) - Not Clickable */}
      {finalAsset.audience_rune && <InfoCard title={finalAsset.audience_rune.title} content={finalAsset.audience_rune.content} />}
      
      {/* Card 3: The Scribe's Sigils (Platform Setup) - Not Clickable */}
      {finalAsset.platform_sigils && <InfoCard title={finalAsset.platform_sigils.title} content={finalAsset.platform_sigils.content} />}

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
  
  // The logic for other asset types remains the same.
  const renderHtmlAsset = () => (
    <div className="space-y-8">
      {finalAsset.html_code && <CopyCard title={finalAsset.html_code.title} content={finalAsset.html_code.content} />}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {finalAsset.image_prompts && finalAsset.image_prompts.map((prompt: any, index: number) => (
          <ActionCard key={index} title={`Generate ${prompt.section}`} description={`Invoke a ritual to receive the prompt for the ${prompt.section.toLowerCase()}.`} icon="🖼️" onClick={() => unveilPrompt('Image')} />
        ))}
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