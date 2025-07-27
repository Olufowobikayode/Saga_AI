// --- START OF REFACTORED FILE src/app/anvil/page.tsx ---
'use client'; 

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ArtisanManager from '@/components/ArtisanManager';
import { usePodStore } from '@/store/podStore';
import { useSagaStore } from '@/store/sagaStore';
import StrategySidebar from '@/components/StrategySidebar'; // <-- 1. IMPORT THE NEW COMPONENT

/**
 * The Artisan's Anvil: The main page for the Print-on-Demand Saga Stack.
 * It is now responsible for initializing the podStore with the correct context
 * and displaying the persistent strategy sidebar.
 */
export default function AnvilPage() {
  const router = useRouter();

  const beginForging = usePodStore((state) => state.beginForging);
  const podStatus = usePodStore((state) => state.status);
  const grandStrategyInterest = useSagaStore((state) => state.brief.interest);

  useEffect(() => {
    if (podStatus === 'idle') {
      if (!grandStrategyInterest || grandStrategyInterest.trim() === '') {
        alert("A Grand Strategy is required to use the Artisan's Anvil. Returning to the Altar of Inquiry.");
        router.push('/consult');
      } else {
        beginForging(grandStrategyInterest);
      }
    }
  }, [podStatus, grandStrategyInterest, beginForging, router]);
  
  return (
    // Add relative positioning to the main container for the sidebar's context
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4 relative"> 
      
      {/* --- 2. ADD THE SIDEBAR COMPONENT HERE --- */}
      <StrategySidebar />

      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Artisan's Anvil
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Forge Designs of Legend: Print-on-Demand Opportunities
          </p>
        </header>

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