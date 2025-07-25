// --- START OF FILE src/app/ledger/page.tsx ---
'use client'; // This page is the root of a complex client-side workflow.

import React, { useEffect } from 'react';
import Link from 'next/link';
import LedgerManager from '@/components/LedgerManager'; // Summoning the Ledger Manager.
import { useCommerceStore } from '@/store/commerceStore';

/**
 * The Hall of Commerce: The main page for the Commerce Saga Stack.
 * All of its multi-stage logic is now governed by the LedgerManager.
 */
export default function LedgerPage() {
  // SAGA LOGIC: Connect to the store to begin the entry ritual when the user arrives.
  const enterLedger = useCommerceStore((state) => state.enterLedger);
  const status = useCommerceStore((state) => state.status);

  // When this page loads for the first time, begin the sacred entry ritual.
  useEffect(() => {
    // The 'idle' check ensures this rite is only performed once upon entry.
    if (status === 'idle') {
      enterLedger();
    }
  }, [status, enterLedger]);

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
          The LedgerManager now presides over this hall. It will read from the
          commerceStore and unveil the correct UI for the user's current stage.
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
// --- END OF FILE src/app/ledger/page.tsx ---