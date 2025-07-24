// --- START OF FILE src/components/FinalScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';
import SagaButton from './SagaButton';

// --- Helper Components ---

// BaseCard provides a consistent container for all prophecy pieces.
const BaseCard = ({ title, children }: { title: string, children: React.ReactNode }) => (
    <div className="bg-saga-surface p-6 rounded-lg border border-white/10 h-full">
        <h3 className="font-serif text-xl font-bold text-saga-secondary mb-4">{title}</h3>
        {children}
    </div>
);

// Renders the main content with Copy and Regenerate buttons.
const ContentWithActionsCard = ({ title, content, isCode = false }: { title: string; content: string; isCode?: boolean }) => {
    const { regenerateAsset, status } = useMarketingStore();
    const isLoading = status === 'forging_asset';

    const handleCopy = () => navigator.clipboard.writeText(content);

    return (
        <BaseCard title={title}>
            {isCode ? (
                <pre className="text-saga-text-dark whitespace-pre-wrap font-mono bg-saga-bg p-4 rounded-md text-sm overflow-x-auto">
                    <code>{content}</code>
                </pre>
            ) : (
                <p className="text-saga-text-dark whitespace-pre-wrap font-sans">{content}</p>
            )}
            <div className="flex items-center space-x-4 mt-6 pt-4 border-t border-white/10">
                <button onClick={handleCopy} className="text-sm font-semibold text-saga-primary hover:text-saga-secondary">Copy</button>
                <button onClick={regenerateAsset} className="text-sm font-semibold text-saga-primary hover:text-saga-secondary flex items-center">
                    {isLoading ? 'Regenerating...' : 'Regenerate'}
                    {!isLoading && <span className="ml-1">✨</span>}
                </button>
            </div>
        </BaseCard>
    );
};

// Renders info cards (like Audience Rune) which don't need actions.
const InfoCard = ({ title, content }: { title: string; content: object }) => (
    <BaseCard title={title}>
        <ul className="space-y-3">
            {Object.entries(content).map(([key, value]) => (
                <li key={key} className="text-saga-text-dark leading-relaxed">
                    <strong className="block text-saga-text-light font-semibold">{key.replace(/_/g, ' ')}:</strong>
                    <span>{Array.isArray(value) ? value.join(', ') : String(value)}</span>
                </li>
            ))}
        </ul>
    </BaseCard>
);

// Renders clickable cards for generating new assets.
const ActionCard = ({ title, description, icon, onClick }: { title: string; description: string; icon: string; onClick: () => void; }) => (
    <button onClick={onClick} className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 text-left hover:border-saga-primary hover:scale-105 transition-all duration-300">
        <div className="text-4xl mb-4">{icon}</div>
        <h3 className="font-serif text-xl font-bold text-saga-secondary mb-2">{title}</h3>
        <p className="text-saga-text-dark">{description}</p>
    </button>
);


export default function FinalScroll() {
  const { finalAsset, chosenAssetType, resetForge, unveilPrompt, unfurlScroll } = useMarketingStore();

  if (!finalAsset) {
    return <div className="text-center p-8">The prophecy is faint... No asset was found.</div>;
  }

  const renderTextAsset = () => (
    <div className="space-y-8">
      {finalAsset.copy && <ContentWithActionsCard title={finalAsset.copy.title} content={finalAsset.copy.content} />}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {finalAsset.audience_rune && <InfoCard title={finalAsset.audience_rune.title} content={finalAsset.audience_rune.content} />}
        {finalAsset.platform_sigils && <InfoCard title={finalAsset.platform_sigils.title} content={finalAsset.platform_sigils.content} />}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {finalAsset.image_orb && <ActionCard title={finalAsset.image_orb.title} description={finalAsset.image_orb.description} icon="🖼️" onClick={() => unveilPrompt('Image')} />}
        {finalAsset.motion_orb && <ActionCard title={finalAsset.motion_orb.title} description={finalAsset.motion_orb.description} icon="🎬" onClick={() => unveilPrompt('Video')} />}
      </div>
    </div>
  );
  
  const renderHtmlAsset = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <ActionCard title="View HTML Code" description="Unfurl the scroll containing the complete, SEO-optimized HTML for your page." icon="📜" onClick={() => unfurlScroll('html_code')} />
        <ActionCard title="View Deployment Guide" description="Unfurl the scroll with custom, step-by-step instructions for deploying your page." icon="🗺️" onClick={() => unfurlScroll('deployment_guide')} />
        {finalAsset.image_prompts && finalAsset.image_prompts.map((prompt: any, index: number) => (
          <ActionCard key={index} title={`Generate ${prompt.section}`} description={`Invoke a ritual for the ${prompt.section.toLowerCase()} prompt.`} icon="🖼️" onClick={() => unveilPrompt('Image')} />
        ))}
    </div>
  );

  const renderReviewAsset = () => (
    <div className="space-y-8">
      {finalAsset.reviews && finalAsset.reviews.map((review: any, index: number) => (
        <ContentWithActionsCard key={index} title={review.title} content={review.content} />
      ))}
    </div>
  );
  
  const renderAsset = () => {
    switch (chosenAssetType) {
      case 'Funnel Page': case 'Landing Page': return renderHtmlAsset();
      case 'Affiliate Review': return renderReviewAsset();
      default: return renderTextAsset();
    }
  };

  return (
    <motion.div key="final-scroll" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">The Prophecy is Inscribed</h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          {chosenAssetType === 'Funnel Page' || chosenAssetType === 'Landing Page' ?
            "The blueprints are forged. Unfurl the scrolls to reveal their secrets." :
            "Wield these words of power as you see fit."
          }
        </p>
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