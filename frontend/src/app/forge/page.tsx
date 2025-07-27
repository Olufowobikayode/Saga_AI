// --- START OF REFACTORED FILE src/app/forge/page.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ForgeManager from '@/components/ForgeManager';
import { useMarketingStore } from '@/store/marketingStore';
import { useSagaStore } from '@/store/sagaStore';
import StrategySidebar from '@/components/StrategySidebar'; // <-- 1. IMPORT THE SIDEBAR

/**
 * The Skald's Forge: The main page for the Marketing Saga Stack.
 * It is now responsible for initializing the marketingStore and displaying the sidebar.
 */
export default function ForgePage() {
  const router = useRouter();

  const invokeForge = useMarketingStore((state) => state.invokeForge);
  const marketingStatus = useMarketingStore((state) => state.status);
  const grandStrategyInterest = useSagaStore((state) => state.brief.interest);

  useEffect(() => {
    if (marketingStatus === 'idle') {
      if (!grandStrategyInterest || grandStrategyInterest.trim() === '') {
        alert("A Grand Strategy is required to use the Skald's Forge. Returning to the Altar of Inquiry.");
        router.push('/consult');
      } else {
        invokeForge();
      }
    }
  }, [marketingStatus, grandStrategyInterest, invokeForge, router]);

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4 relative">
      
      {/* --- 2. ADD THE SIDEBAR COMPONENT HERE --- */}
      <StrategySidebar />

      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Skald's Forge
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Weave Words of Power: Ads, Funnels, & Persuasion
          </p>
        </header>

        <ForgeManager />

        <div className="text-center mt-16">
          <Link href="/consult" className="font-serif text-xl text-saga-text-dark hover:text-saga-primary transition-colors">
            ← Return to the Hall of Prophecies
          </Link>
        </div>

      </div>
    </div>
  );
}
// --- END OF REFACTORED FILE src/app/forge/page.tsx ---