// --- START OF FILE frontend/src/components/AltarManager.tsx ---
'use client';

import React from 'react';
import { useSagaStore } from '@/store/sagaStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import QueryForm from './QueryForm';
import ArtifactForm from './ArtifactForm';
import RealmForm from './RealmForm';
import HallOfProphecies from './HallOfProphecies';

/**
 * AltarManager: The master controller for the multi-stage Grand Strategic Ritual.
 * It reads the status from the main sagaStore and renders the correct UI for each stage.
 */
export default function AltarManager() {
  const status = useSagaStore((state) => state.status);
  const ritualPromise = useSagaStore((state) => state.ritualPromise);

  // A handler to be called by RitualScreen when it completes
  const handleRitualComplete = () => {
    console.log("AltarManager acknowledges ritual completion.");
    // In this specific manager, the store handles the state transition automatically
    // upon promise resolution. So, this function can be empty or used for logging.
  };

  const renderCurrentStage = () => {
    switch (status) {
      // Stage 1: The Query
      case 'awaiting_query':
        return <QueryForm />;
      case 'performing_rite_1':
        // CORRECTED: Pass the required props to RitualScreen
        return (
          <RitualScreen
            key="rite1"
            ritualPromise={ritualPromise}
            onRitualComplete={handleRitualComplete}
          />
        );

      // Stage 2: The Artifact
      case 'awaiting_artifact':
        return <ArtifactForm />;
      case 'performing_rite_2':
        // CORRECTED: Pass the required props to RitualScreen
        return (
          <RitualScreen
            key="rite2"
            ritualPromise={ritualPromise}
            onRitualComplete={handleRitualComplete}
          />
        );

      // Stage 3: The Realm
      case 'awaiting_realm':
        return <RealmForm />;
      case 'performing_grand_rite':
        // CORRECTED: Pass the required props to RitualScreen
        return (
          <RitualScreen
            key="grandrite"
            ritualPromise={ritualPromise}
            onRitualComplete={handleRitualComplete}
          />
        );

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
// --- END OF FILE frontend/src/components/AltarManager.tsx ---