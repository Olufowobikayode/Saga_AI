// --- START OF FILE src/components/SeerManager.tsx ---
'use client';

import React from 'react';
import { useVentureStore } from '@/store/ventureStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import ConfirmationChamber from './ConfirmationChamber';
import HallOfVisions from './HallOfVisions'; // Summoning the real Hall of Visions.

// We will create this final component in the next step.
// For now, it is a placeholder.
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
        return <ConfirmationChamber />;
      case 'questing_for_visions':
        return <RitualScreen />;
      case 'visions_revealed':
        // Now rendering the real component instead of the placeholder.
        return <HallOfVisions />;

      // Phase 2: The Blueprint
      case 'forging_blueprint':
        return <RitualScreen />;
      case 'blueprint_revealed':
        return <BlueprintScroll />;

      // Default/Idle State
      default:
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