// --- START OF FILE frontend/src/components/ArtisanManager.tsx ---
'use client';

import React from 'react';
import { usePodStore } from '@/store/podStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import StyleChamber from './StyleChamber';
import HallOfConcepts from './HallOfConcepts';
import DesignPackageScroll from './DesignPackageScroll';

/**
 * ArtisanManager: The master controller for the entire Print-on-Demand workflow.
 * It reads the status from the podStore and renders the appropriate UI.
 */
export default function ArtisanManager() {
  const status = usePodStore((state) => state.status);
  const ritualPromise = usePodStore((state) => state.ritualPromise);

  const handleRitualComplete = () => {
    console.log("ArtisanManager acknowledges ritual completion.");
    // The store manages its own state transitions upon promise resolution.
  };

  const renderCurrentStage = () => {
    switch (status) {
      // Phase 1: The Opportunity Hunt
      case 'awaiting_style':
        return <StyleChamber />;
      
      case 'concepts_revealed':
        return <HallOfConcepts />;

      // Phase 2: The Design Package
      case 'package_revealed':
        return <DesignPackageScroll />;

      // Ritual States
      case 'hunting_opportunities':
      case 'forging_package':
        // CORRECTED: Pass the required props to RitualScreen
        return (
          <RitualScreen
            key={`artisan-ritual-${status}`}
            ritualPromise={ritualPromise}
            onRitualComplete={handleRitualComplete}
          />
        );

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
// --- END OF FILE frontend/src/components/ArtisanManager.tsx ---