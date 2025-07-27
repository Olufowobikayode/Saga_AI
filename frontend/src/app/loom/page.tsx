// --- START OF REFACTORED FILE src/app/loom/page.tsx ---
'use client'; 

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import WeaverManager from '@/components/WeaverManager';
import { useContentStore } from '@/store/contentStore';
import { useSagaStore } from '@/store/sagaStore';

/**
 * The Weaver's Loom: The main page for the Content Saga Stack.
 * It is now responsible for initializing the contentStore with the correct context.
 */
export default function LoomPage() {
  const router = useRouter();

  // Get the initialization function from the contentStore
  const beginWeaving = useContentStore((state) => state.beginWeaving);
  // Get the current status to prevent re-initialization
  const contentStatus = useContentStore((state) => state.status);
  
  // Get the full strategy data from the main sagaStore
  const grandStrategyData = useSagaStore((state) => state.strategyData);

  // This effect runs once when the page loads, acting as the "Context Bridge".
  useEffect(() => {
    if (contentStatus === 'idle') {
      // If the user lands here directly, the strategy data will be missing.
      if (!grandStrategyData || !grandStrategyData.prophecy) {
        // Redirect them back to the start.
        alert("A Grand Strategy is required to use the Weaver's Loom. Returning to the Altar of Inquiry.");
        router.push('/consult');
      } else {
        // If we have context, initialize the contentStore with it.
        // We derive the initial topic from the strategy, but the user can change it.
        const tacticalInterest = grandStrategyData.prophecy?.the_three_great_sagas[1]?.prime_directive || grandStrategyData.prophecy?.divine_summary || 'a compelling topic';
        
        beginWeaving(grandStrategyData, tacticalInterest);
      }
    }
  }, [contentStatus, grandStrategyData, beginWeaving, router]);

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Weaver's Loom
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Craft Sagas for Any Realm: Posts, Blogs, & Comments
          </p>
        </header>

        {/* 
          The WeaverManager will now operate with the correct context
          or the user will have been redirected.
        */}
        <WeaverManager />

        <div className="text-center mt-16">
          <Link href="/consult" className="font-serif text-xl text-saga-text-dark hover:text-saga-primary transition-colors">
            ← Return to the Hall of Prophecies
          </Link>
        </div>
      </div>
    </div>
  );
}
// --- END OF REFACTORED FILE src/app/loom/page.tsx ---