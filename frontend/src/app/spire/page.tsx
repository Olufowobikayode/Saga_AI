// --- START OF REFACTORED FILE src/app/spire/page.tsx ---
'use client'; 

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import VentureManager from '@/components/VentureManager';
import { useVentureStore } from '@/store/ventureStore';
import { useSagaStore } from '@/store/sagaStore';

/**
 * The Seer's Spire: The main page for the New Ventures Stack.
 * It is now responsible for initializing the ventureStore with the correct context.
 */
export default function SpirePage() {
  const router = useRouter();

  // Get the initialization function from the ventureStore
  const enterSpire = useVentureStore((state) => state.enterSpire);
  // Get the current status to prevent re-initialization
  const ventureStatus = useVentureStore((state) => state.status);
  
  // Get the ENTIRE brief context from the main sagaStore
  const grandStrategyBrief = useSagaStore((state) => state.brief);

  // This effect runs once when the page loads, acting as the "Context Bridge".
  useEffect(() => {
    // Only initialize if the store is in its default 'idle' state.
    if (ventureStatus === 'idle') {
      // If the user lands here directly, the core interest will be missing.
      if (!grandStrategyBrief || !grandStrategyBrief.interest || grandStrategyBrief.interest.trim() === '') {
        // Redirect them back to the start.
        alert("A Grand Strategy is required to use the Seer's Spire. Returning to the Altar of Inquiry.");
        router.push('/consult');
      } else {
        // If we have context, initialize the ventureStore with it.
        // We pass the whole brief object as the ventureStore needs all of it.
        enterSpire(grandStrategyBrief);
      }
    }
  }, [ventureStatus, grandStrategyBrief, enterSpire, router]);

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
          The VentureManager will now operate with the correct context
          or the user will have been redirected.
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
// --- END OF REFACTORED FILE src/app/spire/page.tsx ---