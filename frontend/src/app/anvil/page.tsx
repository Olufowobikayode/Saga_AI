// --- START OF FILE src/app/anvil/page.tsx ---
'use client'; // This page is the root of a complex client-side workflow.

import React, { useEffect } from 'react';
import Link from 'next/link';
import ArtisanManager from '@/components/ArtisanManager'; // Summoning the Artisan Manager.
import { usePodStore } from '@/store/podStore';

/**
 * The Artisan's Anvil: The main page for the Print-on-Demand Saga Stack.
 * All of its complex, two-phase logic is handled by the ArtisanManager.
 */
export default function AnvilPage() {
  // SAGA LOGIC: Connect to the pod store to begin the forging process.
  const beginForging = usePodStore((state) => state.beginForging);
  const status = usePodStore((state) => state.status);

  // When this page loads for the first time, begin the forging ritual.
  useEffect(() => {
    if (status === 'idle') {
      beginForging();
    }
  }, [status, beginForging]);

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Page Header */}
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Artisan's Anvil
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Forge Designs of Legend: Print-on-Demand Opportunities
          </p>
        </header>

        {/* 
          The ArtisanManager now controls this entire section. It will read from the
          podStore and display the correct UI for the user's current stage.
        */}
        <ArtisanManager />

        {/* Navigation Link to return to the Hall of Prophecies */}
        <div className="text-center mt-16">
          <Link href="/consult" className="font-serif text-xl text-saga-text-dark hover:text-saga-primary transition-colors">
            ← Return to the Hall of Prophecies
          </Link>
        </div>
      </div>
    </div>
  );
}
// --- END OF FILE src/app/anvil/page.tsx ---