// --- START OF FILE src/app/loom/page.tsx ---
'use client'; // This page is the root of a complex client-side workflow.

import React, { useEffect } from 'react';
import Link from 'next/link';
import WeaverManager from '@/components/WeaverManager'; // Summoning the Weaver Manager.
import { useContentStore } from '@/store/contentStore';
import { useSagaStore } from '@/store/sagaStore'; // We need the master store for initial context.

/**
 * The Weaver's Loom: The main page for the Content Saga Stack.
 * All of its complex, multi-stage logic is handled by the WeaverManager.
 */
export default function LoomPage() {
  // SAGA LOGIC: Connect to both the master and the content stores.
  const beginWeaving = useContentStore((state) => state.beginWeaving);
  const status = useContentStore((state) => state.status);
  const grandStrategyData = useSagaStore((state) => state.strategyData);

  // When this page loads, we pass the strategic context from the master store
  // to the content store to begin the weaving process.
  useEffect(() => {
    if (status === 'idle' && grandStrategyData) {
      // For now, we'll pick the first content pillar's tactical interest as the default.
      // A more advanced UI would let the user choose which pillar to work on.
      const tacticalInterest = grandStrategyData.prophecy?.content_pillars?.[0]?.tactical_interest || 'a topic of interest';
      
      beginWeaving(grandStrategyData, tacticalInterest);
    }
  }, [status, beginWeaving, grandStrategyData]);

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Page Header */}
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Weaver's Loom
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Craft Sagas for Any Realm: Posts, Blogs, & Comments
          </p>
        </header>

        {/* 
          The WeaverManager now controls this entire section. It will read from the
          contentStore and display the correct UI for the user's current stage.
        */}
        <WeaverManager />

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
// --- END OF FILE src/app/loom/page.tsx ---