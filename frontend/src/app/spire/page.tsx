// --- START OF FILE src/app/spire/page.tsx ---
'use client'; // This page is the root of a complex client-side workflow.

import React from 'react';
import Link from 'next/link';
import SeerManager from '@/components/SeerManager'; // Summoning the Seer Manager.

/**
 * The Seer's Spire: The main page for the New Ventures Stack.
 * All of its complex, two-phase logic is handled by the SeerManager.
 */
export default function SpirePage() {
  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Page Header */}
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Seer's Spire
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Gaze Into What May Be: Discover & Plan New Ventures
          </p>
        </header>

        {/* 
          The SeerManager now controls this entire section. It will read from the
          ventureStore and display the correct UI for the user's current stage.
        */}
        <SeerManager />

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
// --- END OF FILE src/app/spire/page.tsx ---