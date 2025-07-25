// --- START OF FILE frontend/src/components/VentureManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useVentureStore } from '@/store/ventureStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import RefinementChamber from './RefinementChamber';
import HallOfVisions from './HallOfVisions';
import BlueprintScroll from './BlueprintScroll';

/**
 * VentureManager: The master controller for the entire New Ventures workflow.
 * It reads the status from the ventureStore and renders the appropriate UI.
 */
export default function VentureManager() {
  const status = useVentureStore((state) => state.status);
  const enterSpire = useVentureStore((state) => state.enterSpire);
  const ritualPromise = useVentureStore((state) => state.ritualPromise);

  useEffect(() => {
    if (status === 'idle') {
      enterSpire();
    }
  }, [status, enterSpire]);

  const handleRitualComplete = () => {
    console.log("VentureManager acknowledges ritual completion.");
    // The store manages its own state transitions upon promise resolution.
  };

  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_refinement':
        return <RefinementChamber />;

      case 'visions_revealed':
        return <HallOfVisions />;

      case 'blueprint_revealed':
        return <BlueprintScroll />;

      case 'performing_entry_rite':
      case 'questing_for_visions':
      case 'forging_blueprint':
        // CORRECTED: Pass the required props to RitualScreen
        return (
          <RitualScreen
            key={`venture-ritual-${status}`}
            ritualPromise={ritualPromise}
            onRitualComplete={handleRitualComplete}
          />
        );

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
// --- END OF FILE frontend/src/components/VentureManager.tsx ---