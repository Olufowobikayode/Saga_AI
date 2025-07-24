// --- START OF FILE src/components/SeerManager.tsx ---
'use client';

import React from 'react';
import { useVentureStore } from '@/store/ventureStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import ConfirmationChamber from './ConfirmationChamber'; // Summoning the real component.

// We will create these new components in the upcoming steps.
// For now, they are placeholders.
const HallOfVisions = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for HallOfVisions</div>;
const BlueprintScroll = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for BlueprintScroll</div>;


/**
 * SeerManager: The master controller for the entire New Ventures workflow.
 * It reads the status from the ventureStore and renders the appropriate UI.
 */
export default function SeerManager() {
  const status = useVentureStore((state) => state.status);

  const renderCurrentStage = () => {
    switch (status) {
      // Phase 1: The Vision Quest
      case 'awaiting_confirmation':
        // Now rendering the real component instead of the placeholder.
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
        // When the page first loads and the store is 'idle', we show the confirmation chamber.
        // It has its own internal ritual logic.
        return <ConfirmationChamber />;
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