// --- START OF FILE src/components/ConfirmationChamber.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';
import { useVentureStore } from '@/store/ventureStore';
import SagaButton from './SagaButton';
import RitualScreen from './RitualScreen';

/**
 * ConfirmationChamber: The first step in the Seer's Spire. Confirms the
 * user's intent to begin the Vision Quest based on their initial query.
 */
export default function ConfirmationChamber() {
  // SAGA LOGIC: Get the necessary state and functions from both stores.
  const { brief } = useSagaStore(); // Get the initial briefing document.
  const { beginQuest, status } = useVentureStore();
  
  // Local state to manage the entry ritual.
  const [showEntryRitual, setShowEntryRitual] = useState(true);

  // SAGA LOGIC: Perform the entry ritual as commanded.
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowEntryRitual(false);
    }, 30000); // 30-second ad ritual.

    // A real implementation would also create the 1x1 pixel ad iframe here.
    console.log("ENTRY RITUAL: Ad iframe would be created now.");

    return () => clearTimeout(timer);
  }, []); // Run only once on component mount.

  if (showEntryRitual) {
    return <RitualScreen />;
  }

  return (
    <motion.div
      key="confirmation-chamber"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg text-center">
        <header className="border-b border-saga-primary/20 pb-6 mb-8">
          <h2 className="font-serif text-3xl text-saga-primary">The Vision Quest</h2>
          <p className="text-saga-text-dark mt-2 max-w-xl mx-auto">
            The Seer will gaze into the mists of the future, seeking new ventures related to the core interest you provided.
          </p>
        </header>

        <div className="my-8">
          <p className="font-serif text-lg text-saga-text-dark">Prophecy will be forged for:</p>
          <p className="font-serif text-4xl text-saga-secondary font-bold mt-2">
            "{brief.interest || 'a topic of great import'}"
          </p>
        </div>

        <div className="pt-4">
          <SagaButton onClick={beginQuest} className="py-3 px-8 text-lg">
            {status === 'questing_for_visions' ? "Observing Ritual..." : "Begin the Vision Quest"}
          </SagaButton>
        </div>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/ConfirmationChamber.tsx ---