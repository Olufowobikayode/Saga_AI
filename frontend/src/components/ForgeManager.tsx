// --- START OF FILE src/components/ForgeManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useMarketingStore } from '@/store/marketingStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen'; // We will reuse our magnificent RitualScreen

// We will create these new components in the upcoming steps.
// For now, we'll use placeholders.
const AnvilForm = () => <div className="text-center p-8 bg-saga-surface rounded-lg">Placeholder for Anvil Form (Product Input)</div>;
const HallOfAngles = () => <div className="text-center p-8 bg-saga-surface rounded-lg">Placeholder for Hall of Angles (Asset Type Selection)</div>;
const FinalScroll = () => <div className="text-center p-8 bg-saga-surface rounded-lg">Placeholder for Final Scroll (Asset Display)</div>;


/**
 * ForgeManager: The master controller for the entire Skald's Forge workflow.
 * It reads the status from the marketingStore and renders the appropriate UI.
 */
export default function ForgeManager() {
  // SAGA LOGIC: Connect to the Mind of the Skald.
  const status = useMarketingStore((state) => state.status);
  const invokeForge = useMarketingStore((state) => state.invokeForge);

  // SAGA LOGIC: When the manager first appears, it invokes the entry ritual.
  useEffect(() => {
    // We only want to run the entry ritual once when the component mounts.
    // The 'idle' status check prevents it from re-running on subsequent renders.
    if (status === 'idle') {
      // For now, we will just set the state. We will add the ritual later.
      invokeForge();
    }
  }, [status, invokeForge]);

  // This function will decide which main component to show.
  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_anvil':
        return <AnvilForm />;
      
      case 'angles_revealed':
        return <HallOfAngles />;

      case 'asset_revealed':
        return <FinalScroll />;

      // For all 'forging' states, we show the RitualScreen.
      case 'forging_angles':
      case 'forging_asset':
        return <RitualScreen />;
      
      // Default case for 'idle' or any other state.
      default:
        // We can show a brief loading state or the form itself.
        // Let's show a simple loading message before the anvil form appears.
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