// --- START OF REFACTORED FILE src/app/anvil/page.tsx ---
'use client'; 

import React, 'useEffect } from 'react';
import { useRouter } from 'next/navigation'; // Import router for redirection
import Link from 'next/link';
import ArtisanManager from '@/components/ArtisanManager';
import { usePodStore } from '@/store/podStore';
import { useSagaStore } from '@/store/sagaStore'; // We still need this to GET the context

/**
 * The Artisan's Anvil: The main page for the Print-on-Demand Saga Stack.
 * It is now responsible for initializing the podStore with the correct context.
 */
export default function AnvilPage() {
  const router = useRouter();

  // Get the initialization function from the podStore
  const beginForging = usePodStore((state) => state.beginForging);
  // Get the current status to prevent re-initialization
  const podStatus = usePodStore((state) => state.status);
  
  // Get the context from the main sagaStore
  const grandStrategyInterest = useSagaStore((state) => state.brief.interest);

  // This effect runs once when the page loads.
  // It is the new "Context Bridge" between the Grand Strategy and the Anvil.
  useEffect(() => {
    // Only initialize if the store is in its default 'idle' state.
    if (podStatus === 'idle') {
      // If the user lands here directly without a Grand Strategy, their interest will be empty.
      if (!grandStrategyInterest || grandStrategyInterest.trim() === '') {
        // Redirect them back to the start to get a strategy first.
        alert("A Grand Strategy is required to use the Artisan's Anvil. Returning to the Altar of Inquiry.");
        router.push('/consult');
      } else {
        // If we have context, initialize the podStore with it.
        beginForging(grandStrategyInterest);
      }
    }
    // The dependency array ensures this effect runs if the core data changes.
  }, [podStatus, grandStrategyInterest, beginForging, router]);
  
  // The rest of the page remains the same, but is now context-aware.

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Artisan's Anvil
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Forge Designs of Legend: Print-on-Demand Opportunities
          </p>
        </header>

        {/* 
          The ArtisanManager will now operate with the correct context,
          or the user will have been redirected if they arrived without it.
        */}
        <ArtisanManager />

        <div className="text-center mt-16">
          <Link href="/consult" className="font-serif text-xl text-saga-text-dark hover:text-saga-primary transition-colors">
            ← Return to the Hall of Prophecies
          </Link>
        </div>
      </div>
    </div>
  );
}
// --- END OF REFACTORED FILE src/app/anvil/page.tsx ---