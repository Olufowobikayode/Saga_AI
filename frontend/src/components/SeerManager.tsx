// --- START OF FILE src/components/SeerManager.tsx ---
'use client';

import React from 'react';
import { useVentureStore } from '@/store/ventureStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';

// We will create these new components in the upcoming steps.
// For now, they are placeholders.
const ConfirmationChamber = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for ConfirmationChamber</div>;
const HallOfVisions = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for HallOfVisions</div>;
const BlueprintScroll = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for BlueprintScroll</div>;


/**
 * SeerManager: The master controller for the entire New Ventures workflow.
 * It reads the status from the ventureStore and renders the appropriate UI.
 */
export default function SeerManager() {
  // SAGA LOGIC: Connect to the Mind of the Seer.
  const status = useVentureStore((state) => state.status);

  // This function will decide which component to show based on the prophecy's stage.
  const renderCurrentStage = () => {
    switch (status) {
      // Phase 1: The Vision Quest
      case 'awaiting_confirmation':
        return <ConfirmationChamber />;
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
        // We can show a simple loading state while the store initializes.
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