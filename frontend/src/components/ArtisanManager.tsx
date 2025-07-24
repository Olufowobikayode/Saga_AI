// --- START OF FILE src/components/ArtisanManager.tsx ---
'use client';

import React from 'react';
import { usePodStore } from '@/store/podStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import StyleChamber from './StyleChamber';
import HallOfConcepts from './HallOfConcepts';
import DesignPackageScroll from './DesignPackageScroll'; // Summoning the real Design Package Scroll.

/**
 * ArtisanManager: The master controller for the entire Print-on-Demand workflow.
 * It reads the status from the podStore and renders the appropriate UI.
 */
export default function ArtisanManager() {
  const status = usePodStore((state) => state.status);

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
        // Now rendering the real component instead of the placeholder.
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