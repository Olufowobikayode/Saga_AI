// --- START OF FILE src/components/ForgeManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useMarketingStore } from '@/store/marketingStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import AnvilForm from './AnvilForm'; // Summoning the real AnvilForm.

// We will create these new components in the upcoming steps.
// For now, we'll use placeholders.
const HallOfAngles = () => <div className="text-center p-8 bg-saga-surface rounded-lg">Placeholder for Hall of Angles (Asset Type Selection)</div>;
const FinalScroll = () => <div className="text-center p-8 bg-saga-surface rounded-lg">Placeholder for Final Scroll (Asset Display)</div>;


/**
 * ForgeManager: The master controller for the entire Skald's Forge workflow.
 * It reads the status from the marketingStore and renders the appropriate UI.
 */
export default function ForgeManager() {
  const status = useMarketingStore((state) => state.status);
  const invokeForge = useMarketingStore((state) => state.invokeForge);

  useEffect(() => {
    if (status === 'idle') {
      // For now, we will just set the state. We will add the ritual later.
      invokeForge();
    }
  }, [status, invokeForge]);

  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_anvil':
        // Now rendering the real form instead of the placeholder.
        return <AnvilForm />;
      
      case 'angles_revealed':
        return <HallOfAngles />;

      case 'asset_revealed':
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