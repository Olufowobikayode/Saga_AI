// --- START OF FILE src/components/AltarManager.tsx ---
'use client';

import React from 'react';
import { useSagaStore } from '@/store/sagaStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import QueryForm from './QueryForm';
import ArtifactForm from './ArtifactForm'; // Summoning the real Artifact Form.

// We will create this new form component in the upcoming step.
// For now, it is a placeholder.
const RealmForm = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for Realm Form</div>;

// The Hall of Prophecies will be shown at the end.
const HallOfProphecies = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for Hall of Prophecies</div>;


/**
 * AltarManager: The master controller for the multi-stage Grand Strategic Ritual.
 * It reads the status from the main sagaStore and renders the correct UI for each stage.
 */
export default function AltarManager() {
  const status = useSagaStore((state) => state.status);

  const renderCurrentStage = () => {
    switch (status) {
      // Stage 1: The Query
      case 'awaiting_query':
        return <QueryForm />;
      case 'performing_rite_1':
        return <RitualScreen />;

      // Stage 2: The Artifact
      case 'awaiting_artifact':
        // Now rendering the real form instead of the placeholder.
        return <ArtifactForm />;
      case 'performing_rite_2':
        return <RitualScreen />;

      // Stage 3: The Realm
      case 'awaiting_realm':
        return <RealmForm />;
      case 'performing_grand_rite':
        return <RitualScreen />;

      // The Final Destination
      case 'prophesied':
        return <HallOfProphecies />;

      // Default/Idle State
      default:
        return <div className="text-center p-8">Awaiting the beginning of the ritual...</div>;
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
// --- END OF FILE src/components/AltarManager.tsx ---