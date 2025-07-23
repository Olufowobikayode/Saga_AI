// --- START OF FILE src/app/forge/page.tsx ---
import React from 'react';
import Link from 'next/link';

/**
 * The Skald's Forge: The main page for the Marketing Saga Stack.
 * This is where users will generate all marketing-related prophecies.
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
          This is where the main logic for this page will go.
          We will build a "manager" component for this page, just like we did for the
          consultation page, to handle the different states:
          1. Show the initial form to get marketing angles.
          2. Show a loading screen while angles are generated.
          3. Show the generated "Angle Cards" for the user to choose from.
          4. Show the final generated asset.
        */}
        <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
          <p className="text-center text-saga-text-dark">
            [The form for generating Marketing Angles will appear here.]
          </p>
        </div>

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