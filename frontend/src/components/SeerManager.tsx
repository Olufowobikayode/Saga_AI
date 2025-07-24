// --- START OF FILE src/components/SeerManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useVentureStore } from '@/store/ventureStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import RefinementChamber from './RefinementChamber'; // Summoning the new, superior component.
import HallOfVisions from './HallOfVisions';
import BlueprintScroll from './BlueprintScroll';

/**
 * SeerManager: The master controller for the entire New Ventures workflow.
 * It reads the status from the ventureStore and renders the appropriate UI.
 */
export default function SeerManager() {
  // SAGA LOGIC: Connect to the Mind of the Seer.
  const { status, enterSpire } = useVentureStore();

  // When the manager first appears, it invokes the entry rite.
  useEffect(() => {
    if (status === 'idle') {
      enterSpire();
    }
  }, [status, enterSpire]);


  // This function will decide which component to show based on the prophecy's stage.
  const renderCurrentStage = () => {
    switch (status) {
      // Phase 1: The Vision Quest
      case 'awaiting_refinement':
        // Now rendering the RefinementChamber instead of the old ConfirmationChamber.
        return <RefinementChamber />;
      case 'questing_for_visions':
        return <RitualScreen />;
      case 'visions_revealed':
        return <HallOfVisions />;

      // Phase 2: The Blueprint
      case 'forging_blueprint':
        return <RitualScreen />;
      case 'blueprint_revealed':
        return <BlueprintScroll />;

      // Default/Idle State
      default:
        return <div className="text-center p-8">Preparing the Seer's Spire...</div>;
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
// --- END OF FILE src/components/SeerManager.tsx ---