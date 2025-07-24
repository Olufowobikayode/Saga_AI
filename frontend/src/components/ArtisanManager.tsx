// --- START OF FILE src/components/ArtisanManager.tsx ---
'use client';

import React from 'react';
import { usePodStore } from '@/store/podStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import StyleChamber from './StyleChamber';
import HallOfConcepts from './HallOfConcepts'; // Summoning the real Hall of Concepts.

// We will create this final component in the next step.
// For now, it is a placeholder.
const DesignPackageScroll = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for DesignPackageScroll</div>;


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
        // Now rendering the real component instead of the placeholder.
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