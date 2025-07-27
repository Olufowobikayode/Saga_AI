// --- START OF REFACTORED FILE src/app/spire/page.tsx ---
'use client'; 

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import VentureManager from '@/components/VentureManager';
import { useVentureStore } from '@/store/ventureStore';
import { useSagaStore } from '@/store/sagaStore';
import StrategySidebar from '@/components/StrategySidebar'; // <-- 1. IMPORT THE SIDEBAR

/**
 * The Seer's Spire: The main page for the New Ventures Stack.
 * It is now responsible for initializing the ventureStore and displaying the sidebar.
 */
export default function SpirePage() {
  const router = useRouter();

  const enterSpire = useVentureStore((state) => state.enterSpire);
  const ventureStatus = useVentureStore((state) => state.status);
  const grandStrategyBrief = useSagaStore((state) => state.brief);

  useEffect(() => {
    if (ventureStatus === 'idle') {
      if (!grandStrategyBrief || !grandStrategyBrief.interest || grandStrategyBrief.interest.trim() === '') {
        alert("A Grand Strategy is required to use the Seer's Spire. Returning to the Altar of Inquiry.");
        router.push('/consult');
      } else {
        enterSpire(grandStrategyBrief);
      }
    }
  }, [ventureStatus, grandStrategyBrief, enterSpire, router]);

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4 relative">
     
      {/* --- 2. ADD THE SIDEBAR COMPONENT HERE --- */}
      <StrategySidebar />

      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Seer's Spire
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Gaze Into What May Be: Discover & Plan New Ventures
          </p>
        </header>

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