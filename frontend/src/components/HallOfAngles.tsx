// --- START OF REFACTORED FILE frontend/src/components/HallOfAngles.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';

const assetTypes = [
  { id: 'Ad Copy', title: "Ad Copy", description: "Forge persuasive copy for social media and search engine ads.", icon: "🎯" },
  { id: 'Email Copy', title: "Email Copy", description: "Compose high-open-rate emails for newsletters and campaigns.", icon: "✉️" },
  { id: 'Affiliate Copy', title: "Affiliate Copy", description: "Craft compelling messages for your partners to share.", icon: "🤝" },
  { id: 'Funnel Page', title: "Funnel Page", description: "Generate the complete HTML for a high-converting funnel page.", icon: "🌊" },
  { id: 'Landing Page', title: "Landing Page", description: "Create the full HTML for a beautiful, persuasive landing page.", icon: "🏠" },
  { id: 'Affiliate Review', title: "Affiliate Review", description: "Produce authentic, trustworthy reviews to promote affiliate products.", icon: "⭐" }
];

export default function HallOfAngles() {
  // SAGA LOGIC: Get the 'chooseAssetType' function from the store. This is now a simple state update.
  const chooseAssetType = useMarketingStore((state) => state.chooseAssetType);
  const anglesResult = useMarketingStore((state) => state.anglesResult);

  if (!anglesResult?.marketing_angles || anglesResult.marketing_angles.length === 0) {
      return (
          <div className="text-center p-8 bg-saga-surface rounded-lg">
              <h2 className="font-serif text-3xl text-red-400 mb-4">The Forge is Silent</h2>
              <p className="text-saga-text-dark">Saga could not divine any strategic angles for the provided artifact. Please return to the Anvil and try a different description or target audience.</p>
          </div>
      )
  }

  return (
    <motion.div
      key="hall-of-angles"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Strategic Angles are Revealed
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          The core strategies have been forged. Now, choose the form your weapon shall take.
        </p>
      </header>
      
      {/* Displaying the actual angles from the store for user context */}
      <div className="mb-12 space-y-4">
          {anglesResult.marketing_angles.map((angle) => (
              <div key={angle.angle_id} className="bg-saga-bg p-4 rounded-lg border border-saga-surface">
                  <h3 className="font-semibold text-lg text-saga-primary">{angle.title}</h3>
                  <p className="text-sm text-saga-text-dark">{angle.description}</p>
              </div>
          ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {assetTypes.map((asset, index) => (
          <motion.div
            key={asset.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <button
              // SAGA LOGIC: This now simply sets the asset type in the store and advances the state machine.
              onClick={() => chooseAssetType(asset.id)}
              className="w-full h-full bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg text-left
                         hover:border-saga-primary hover:scale-105 transition-all duration-300"
            >
              <div className="text-4xl mb-4">{asset.icon}</div>
              <h3 className="font-serif text-2xl font-bold text-saga-secondary mb-2">
                {asset.title}
              </h3>
              <p className="text-saga-text-dark leading-relaxed">
                {asset.description}
              </p>
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
// --- END OF REFACTORED FILE frontend/src/components/HallOfAngles.tsx ---