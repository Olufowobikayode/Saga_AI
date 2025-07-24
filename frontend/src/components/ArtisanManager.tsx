// --- START OF FILE src/components/ArtisanManager.tsx ---
'use client';

import React from 'react';
import { usePodStore } from '@/store/podStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';

// We will create these new components in the upcoming steps.
// For now, they are placeholders.
const StyleChamber = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for StyleChamber</div>;
const HallOfConcepts = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for HallOfConcepts</div>;
const DesignPackageScroll = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for DesignPackageScroll</div>;


/**
 * ArtisanManager: The master controller for the entire Print-on-Demand workflow.
 * It reads the status from the podStore and renders the appropriate UI.
 */
export default function ArtisanManager() {
  // SAGA LOGIC: Connect to the Mind of the Artisan.
  const status = usePodStore((state) => state.status);

  // This function will decide which component to show based on the prophecy's stage.
  const renderCurrentStage = () => {
    switch (status) {
      // Phase 1: The Opportunity Hunt
      case 'awaiting_style':
        return <StyleChamber />;
      case 'hunting_opportunities':
        return <RitualScreen />;
      case 'concepts_revealed':
        return <HallOfConcepts />;

      // Phase 2: The Design Package
      case 'forging_package':
        return <RitualScreen />;
      case 'package_revealed':
        return <DesignPackageScroll />;

      // Default/Idle State
      default:
        return <div className="text-center p-8">Preparing the Artisan's Anvil...</div>;
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
// --- END OF FILE src/components/ArtisanManager.tsx ---