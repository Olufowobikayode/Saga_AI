// --- START OF FILE src/components/ConsultationManager.tsx ---
'use client';

import React from 'react';
import { useSagaStore } from '@/store/sagaStore';
import ConsultationForm from './ConsultationForm';
import RitualScreen from './RitualScreen';
import HallOfProphecies from './HallOfProphecies'; // Summoning our new results screen.
import { AnimatePresence } from 'framer-motion';

/**
 * ConsultationManager: This component is the master controller for the consultation process.
 * It reads the application's status from the central store and displays the
 * appropriate UI (the form, the loading ritual, or the results).
 */
export default function ConsultationManager() {
  const status = useSagaStore((state) => state.status);

  return (
    <div className="relative">
      <AnimatePresence mode="wait">
        {/* 
          SAGA LOGIC: Conditional rendering based on the application status.
          - If status is 'idle', we show the form.
          - If status is 'divining', we show the RitualScreen.
          - If status is 'prophesied', we now show the HallOfProphecies.
        */}
        {status === 'idle' && <ConsultationForm />}
        
        {status === 'divining' && <RitualScreen />}

        {status === 'prophesied' && <HallOfProphecies />}
      </AnimatePresence>
    </div>
  );
}
// --- END OF FILE src/components/ConsultationManager.tsx ---