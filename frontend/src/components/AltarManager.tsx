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

  // A handler to be called by RitualScreen when it completes.
  // The store handles the state transition automatically upon promise resolution.
  const handleRitualComplete = () => {
    console.log("AltarManager acknowledges ritual completion.");
  };

  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_query':
        return <QueryForm />;

      case 'awaiting_artifact':
        return <ArtifactForm />;

      case 'awaiting_realm':
        return <RealmForm />;

      case 'forging': // This is the new, single loading state that replaces all previous "performing_rite_*" states.
        return (
          <RitualScreen
            key="forging-rite"
            ritualPromise={ritualPromise}
            onRitualComplete={handleRitualComplete}
          />
        );

      case 'prophesied_hub':
      case 'prophesied_scroll': // Both of these final states now correctly show the HallOfProphecies component.
        return <HallOfProphecies />;

      default:
        // This handles the 'idle' state and any other unexpected states.
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