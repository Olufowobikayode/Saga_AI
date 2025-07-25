// --- START OF FILE src/components/VentureManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useVentureStore } from '@/store/ventureStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';

// Veils for the components we will soon forge.
const RefinementChamber = () => <div className="p-8 bg-saga-surface rounded-lg text-center">Awaiting your strategic refinement...</div>;
const HallOfVisions = () => <div className="p-8 bg-saga-surface rounded-lg text-center">The ten visions are revealed...</div>;
const BlueprintScroll = () => <div className="p-8 bg-saga-surface rounded-lg text-center">The final blueprint is unfurled...</div>;


/**
 * VentureManager: The master controller for the entire New Ventures workflow.
 * It reads the status from the ventureStore and renders the appropriate UI.
 */
export default function VentureManager() {
  const status = useVentureStore((state) => state.status);
  const enterSpire = useVentureStore((state) => state.enterSpire);

  // When the manager first appears, it commands the store to enter the first state.
  useEffect(() => {
    if (status === 'idle') {
      enterSpire();
    }
  }, [status, enterSpire]);

  // This function decides which sacred chamber to unveil.
  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_refinement':
        return <RefinementChamber />;
      
      case 'questing_for_visions':
        return <RitualScreen />;

      case 'visions_revealed':
        return <HallOfVisions />;

      case 'forging_blueprint':
        return <RitualScreen />;

      case 'blueprint_revealed':
        return <BlueprintScroll />;

      default:
        return <div className="text-center p-8">Ascending the Seer's Spire...</div>;
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
// --- END OF FILE src/components/VentureManager.tsx ---