// --- START OF FILE src/app/spire/page.tsx ---
'use client'; // This page is the root of a complex client-side workflow.

import React, { useEffect } from 'react';
import Link from 'next/link';
import VentureManager from '@/components/VentureManager'; // We will create this next.
import { useVentureStore } from '@/store/ventureStore';

/**
 * The Seer's Spire: The main page for the New Ventures Stack.
 * All of its multi-stage logic is governed by the VentureManager.
 */
export default function SpirePage() {
  // SAGA LOGIC: Connect to the store to begin the entry rite when the user arrives.
  // Although the store has an entry rite, the first user action will be on the
  // RefinementChamber, so we don't need to call it here. The manager will handle the flow.

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Seer's Spire
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Gaze Into What May Be: Discover & Plan New Ventures
          </p>
        </header>

        {/* 
          The VentureManager will now preside over this hall. It will read from the
          ventureStore and unveil the correct UI for the user's current stage.
        */}
        <VentureManager />

        <div className="text-center mt-16">
          <Link href="/consult" className="font-serif text-xl text-saga-text-dark hover:text-saga-primary transition-colors">
            ← Return to the Hall of Prophecies
          </Link>
        </div>

      </div>
    </div>
  );
}
// --- END OF FILE src/app/spire/page.tsx ---