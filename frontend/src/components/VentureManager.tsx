// --- START OF FILE src/components/VentureManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useVentureStore } from '@/store/ventureStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import RefinementChamber from './RefinementChamber';
import HallOfVisions from './HallOfVisions'; // Summoning the real Hall of Visions.

// Veil for the final component we will forge.
const BlueprintScroll = () => <div className="p-8 bg-saga-surface rounded-lg text-center">The final blueprint is unfurled...</div>;


/**
 * VentureManager: The master controller for the entire New Ventures workflow.
 * It reads the status from the ventureStore and renders the appropriate UI.
 */
export default function VentureManager() {
  const status = useVentureStore((state) => state.status);
  const enterSpire = useVentureStore((state) => state.enterSpire);

  useEffect(() => {
    if (status === 'idle') {
      enterSpire();
    }
  }, [status, enterSpire]);

  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_refinement':
        return <RefinementChamber />;
      
      case 'questing_for_visions':
        return <RitualScreen />;

      case 'visions_revealed':
        // Now unveiling the real component instead of the veil.
        return <HallOfVisions />;

      case 'forging_blueprint':
        return <RitualScreen />;

      case 'blueprint_revealed':
        return <BlueprintScroll />;

      case 'performing_entry_rite':
        return <RitualScreen />;

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