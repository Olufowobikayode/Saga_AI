// --- START OF REFACTORED FILE src/app/ledger/page.tsx ---
'use client'; 

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import LedgerManager from '@/components/LedgerManager';
import { useCommerceStore } from '@/store/commerceStore';
import { useSagaStore } from '@/store/sagaStore';

/**
 * The Hall of Commerce: The main page for the Commerce Saga Stack.
 * It is now responsible for initializing the commerceStore.
 */
export default function LedgerPage() {
  const router = useRouter();

  // Get the initialization function from the commerceStore
  const enterLedger = useCommerceStore((state) => state.enterLedger);
  // Get the current status to prevent re-initialization
  const commerceStatus = useCommerceStore((state) => state.status);

  // Get the context from the main sagaStore to ensure a strategy exists
  const grandStrategyInterest = useSagaStore((state) => state.brief.interest);

  // This effect runs once when the page loads, acting as the "Context Bridge".
  useEffect(() => {
    if (commerceStatus === 'idle') {
      // If the user lands here directly, the core interest will be missing.
      if (!grandStrategyInterest || grandStrategyInterest.trim() === '') {
        // Redirect them back to the start.
        alert("A Grand Strategy is required to use the Merchant's Ledger. Returning to the Altar of Inquiry.");
        router.push('/consult');
      } else {
        // If context exists, initialize the commerce workflow.
        enterLedger();
      }
    }
  }, [commerceStatus, grandStrategyInterest, enterLedger, router]);

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Merchant's Ledger
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Master the Flow of Coin: Audits, Arbitrage, & Product Routes
          </p>
        </header>

        {/* 
          The LedgerManager will now operate with the correct context
          or the user will have been redirected.
        */}
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