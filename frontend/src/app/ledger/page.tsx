// --- START OF REFACTORED FILE src/app/ledger/page.tsx ---
'use client'; 

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import LedgerManager from '@/components/LedgerManager';
import { useCommerceStore } from '@/store/commerceStore';
import { useSagaStore } from '@/store/sagaStore';
import StrategySidebar from '@/components/StrategySidebar'; // <-- 1. IMPORT THE SIDEBAR

/**
 * The Hall of Commerce: The main page for the Commerce Saga Stack.
 * It is now responsible for initializing the commerceStore and displaying the sidebar.
 */
export default function LedgerPage() {
  const router = useRouter();

  const enterLedger = useCommerceStore((state) => state.enterLedger);
  const commerceStatus = useCommerceStore((state) => state.status);
  const grandStrategyInterest = useSagaStore((state) => state.brief.interest);

  useEffect(() => {
    if (commerceStatus === 'idle') {
      if (!grandStrategyInterest || grandStrategyInterest.trim() === '') {
        alert("A Grand Strategy is required to use the Merchant's Ledger. Returning to the Altar of Inquiry.");
        router.push('/consult');
      } else {
        enterLedger();
      }
    }
  }, [commerceStatus, grandStrategyInterest, enterLedger, router]);

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4 relative">
      
      {/* --- 2. ADD THE SIDEBAR COMPONENT HERE --- */}
      <StrategySidebar />

      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Merchant's Ledger
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Master the Flow of Coin: Audits, Arbitrage, & Product Routes
          </p>
        </header>

        <LedgerManager />

        <div className="text-center mt-16">
          <Link href="/consult" className="font-serif text-xl text-saga-text-dark hover:text-saga-primary transition-colors">
            ← Return to the Hall of Prophecies
          </Link>
        </div>

      </div>
    </div>
  );
}
// --- END OF REFACTORED FILE src/app/ledger/page.tsx ---