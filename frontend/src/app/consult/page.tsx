// --- START OF FILE src/app/consult/page.tsx ---
'use client'; // This page now relies on client-side state, so it must be a client component.

import React, { useEffect } from 'react';
import AltarManager from '@/components/AltarManager'; // Summoning the new Altar Manager.
import { useSagaStore } from '@/store/sagaStore'; // Summoning the master consciousness.

/**
 * The Consultation Chamber: This page now serves as the vessel for the
 * multi-stage Grand Strategic Ritual, orchestrated by the AltarManager.
 */
export default function ConsultPage() {
  // SAGA LOGIC: We connect to the store to begin the ritual when the user arrives.
  const beginGrandRitual = useSagaStore((state) => state.beginGrandRitual);
  const status = useSagaStore((state) => state.status);

  // When this page loads for the first time, begin the ritual.
  useEffect(() => {
    // The 'idle' check ensures this only runs once, not every time the component re-renders.
    if (status === 'idle') {
      beginGrandRitual();
    }
  }, [status, beginGrandRitual]);


  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-3xl mx-auto">
        
        {/* The header is now part of the individual form components to allow it to change. */}
        {/* The AltarManager will now control everything inside this container. */}
        <AltarManager />

      </div>
    </div>
  );
}
// --- END OF FILE src/app/consult/page.tsx ---