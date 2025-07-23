// --- START OF FILE src/components/ForgeManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useMarketingStore } from '@/store/marketingStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import AnvilForm from './AnvilForm';
import HallOfAngles from './HallOfAngles';
import ScribesChamber from './ScribesChamber';
import FinalScroll from './FinalScroll'; // Summoning the real FinalScroll.

/**
 * ForgeManager: The master controller for the entire Skald's Forge workflow.
 * It reads the status from the marketingStore and renders the appropriate UI.
 */
export default function ForgeManager() {
  const status = useMarketingStore((state) => state.status);
  const invokeForge = useMarketingStore((state) => state.invokeForge);
  const chosenAssetType = useMarketingStore((state) => state.chosenAssetType);
  const commandScribe = useMarketingStore((state) => state.commandScribe);

  useEffect(() => {
    if (status === 'idle') {
      invokeForge();
    }
  }, [status, invokeForge]);

  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_anvil':
        return <AnvilForm />;
      
      case 'angles_revealed':
        return <HallOfAngles />;

      case 'awaiting_scribe':
        if (!chosenAssetType) return <div className="text-center p-8">Error: Asset Type not chosen.</div>;
        return (
          <ScribesChamber 
            assetType={chosenAssetType} 
            onLengthSelect={(length) => commandScribe(length)} 
          />
        );

      case 'asset_revealed':
        // Now rendering the real Final Scroll instead of the placeholder.
        return <FinalScroll />;

      case 'forging_angles':
      case 'forging_asset':
        return <RitualScreen />;
      
      default:
        return <div className="text-center p-8">Preparing the Forge...</div>;
    }
  };

  return (
    <div>
      <AnimatePresence mode="wait">
        {renderCurrentStage()}
      </AnimatePresence>
    </div>
  );
}
// --- END OF FILE src/components/ForgeManager.tsx ---