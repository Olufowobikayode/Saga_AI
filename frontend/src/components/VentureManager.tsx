// --- START OF FILE src/components/VentureManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useVentureStore } from '@/store/ventureStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import RefinementChamber from './RefinementChamber';
import HallOfVisions from './HallOfVisions';
import BlueprintScroll from './BlueprintScroll'; // Summoning the real Blueprint Scroll.

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
        return <HallOfVisions />;

      case 'forging_blueprint':
        return <RitualScreen />;

      case 'blueprint_revealed':
        // Now unveiling the real component instead of the veil.
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