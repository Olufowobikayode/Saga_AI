// --- START OF REFACTORED FILE src/app/loom/page.tsx ---
'use client'; 

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import WeaverManager from '@/components/WeaverManager';
import { useContentStore } from '@/store/contentStore';
import { useSagaStore } from '@/store/sagaStore';
import StrategySidebar from '@/components/StrategySidebar'; // <-- 1. IMPORT THE SIDEBAR

/**
 * The Weaver's Loom: The main page for the Content Saga Stack.
 * It is now responsible for initializing the contentStore and displaying the sidebar.
 */
export default function LoomPage() {
  const router = useRouter();

  const beginWeaving = useContentStore((state) => state.beginWeaving);
  const contentStatus = useContentStore((state) => state.status);
  const grandStrategyData = useSagaStore((state) => state.strategyData);

  useEffect(() => {
    if (contentStatus === 'idle') {
      if (!grandStrategyData || !grandStrategyData.prophecy) {
        alert("A Grand Strategy is required to use the Weaver's Loom. Returning to the Altar of Inquiry.");
        router.push('/consult');
      } else {
        const tacticalInterest = grandStrategyData.prophecy?.the_three_great_sagas[1]?.prime_directive || grandStrategyData.prophecy?.divine_summary || 'a compelling topic';
        beginWeaving(grandStrategyData, tacticalInterest);
      }
    }
  }, [contentStatus, grandStrategyData, beginWeaving, router]);

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4 relative">
     
      {/* --- 2. ADD THE SIDEBAR COMPONENT HERE --- */}
      <StrategySidebar />

      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Weaver's Loom
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Craft Sagas for Any Realm: Posts, Blogs, & Comments
          </p>
        </header>

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