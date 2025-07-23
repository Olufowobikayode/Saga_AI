// --- START OF FILE src/components/ConsultationManager.tsx ---
'use client';

import React from 'react';
import { useSagaStore } from '@/store/sagaStore'; // Importing our new state store.
import ConsultationForm from './ConsultationForm';
import RitualScreen from './RitualScreen';
import { AnimatePresence } from 'framer-motion';

/**
 * ConsultationManager: This component is the master controller for the consultation process.
 * It reads the application's status from the central store and displays the
 * appropriate UI (the form, the loading ritual, or the results).
 */
export default function ConsultationManager() {
  // SAGA LOGIC: We subscribe to the 'status' from our store.
  // This component will automatically re-render whenever the status changes.
  const status = useSagaStore((state) => state.status);

  return (
    <div className="relative">
      <AnimatePresence mode="wait">
        {/* 
          SAGA LOGIC: Conditional rendering based on the application status.
          - If status is 'idle', we show the form.
          - If status is 'divining', we show the RitualScreen.
          - If status is 'prophesied', we will show the results (to be built next).
        */}
        {status === 'idle' && <ConsultationForm />}
        
        {status === 'divining' && <RitualScreen />}

        {status === 'prophesied' && (
          <div>
            {/* Placeholder for the Hall of Prophecies (the stack cards) */}
            <p className="text-center text-saga-secondary font-serif text-2xl">
              The Prophecy is Complete. Choose Your Path.
            </p>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
// --- END OF FILE src/components/ConsultationManager.tsx ---