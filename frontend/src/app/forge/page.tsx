// --- START OF FILE src/app/forge/page.tsx ---
import React from 'react';
import Link from 'next/link';
import ForgeManager from '@/components/ForgeManager'; // Summoning the Forge Manager.

/**
 * The Skald's Forge: The main page for the Marketing Saga Stack.
 * All of its complex, multi-stage logic is now handled by the ForgeManager.
 */
export default function ForgePage() {
  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Page Header */}
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Skald's Forge
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Weave Words of Power: Ads, Funnels, & Persuasion
          </p>
        </header>

        {/* 
          The ForgeManager is now placed here. It will read from the marketingStore
          and automatically display the correct UI for the user's current stage
          in the marketing prophecy workflow.
        */}
        <ForgeManager />

        {/* Navigation Link to return to the main hall */}
        <div className="text-center mt-16">
          <Link href="/consult" className="font-serif text-xl text-saga-text-dark hover:text-saga-primary transition-colors">
            ← Return to the Hall of Prophecies
          </Link>
        </div>

      </div>
    </div>
  );
}
// --- END OF FILE src/app/forge/page.tsx ---