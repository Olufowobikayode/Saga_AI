// --- START OF REFACTORED FILE src/components/VentureManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useVentureStore } from '@/store/ventureStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import RefinementChamber from './RefinementChamber';
import HallOfVisions from './HallOfVisions';
import BlueprintScroll from './BlueprintScroll';
// --- 1. IMPORT THE SKELETON COMPONENTS ---
import HallOfVisionsSkeleton from './skeletons/HallOfVisionsSkeleton';
import BlueprintScrollSkeleton from './skeletons/BlueprintScrollSkeleton';


/**
 * VentureManager: The master controller for the entire New Ventures workflow.
 * It now uses skeleton loaders for seamless transitions.
 */
export default function VentureManager() {
  const { status, enterSpire, ritualPromise, visionsResult, blueprint } = useVentureStore();

  useEffect(() => {
    if (status === 'idle') {
      enterSpire();
    }
  }, [status, enterSpire]);

  const handleRitualComplete = () => {
    // This allows the store to transition state, and the manager will react accordingly.
    // The promise resolution in the store already sets the new status.
  };

  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_refinement':
        return <RefinementChamber />;

      // --- 2. ADD SKELETON LOGIC FOR VISIONS ---
      case 'visions_revealed':
        // If the status is correct but the data hasn't populated yet, show a skeleton.
        return visionsResult ? <HallOfVisions /> : <HallOfVisionsSkeleton />;

      // --- 3. ADD SKELETON LOGIC FOR BLUEPRINT ---
      case 'blueprint_revealed':
        // Same pattern for the blueprint view.
        return blueprint ? <BlueprintScroll /> : <BlueprintScrollSkeleton />;

      case 'questing_for_visions':
      case 'forging_blueprint':
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
// --- END OF REFACTORED FILE src/components/VentureManager.tsx ---