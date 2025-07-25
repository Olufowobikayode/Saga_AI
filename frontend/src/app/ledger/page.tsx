// --- START OF FILE src/app/ledger/page.tsx ---
'use client'; // This page is the root of a complex client-side workflow.

import React from 'react';
import Link from 'next/link';
import LedgerManager from '@/components/LedgerManager'; // Summoning the Ledger Manager.

/**
 * The Hall of Commerce: The main page for the Commerce Saga Stack.
 * All of its multi-stage logic is now governed by the LedgerManager.
 */
export default function LedgerPage() {
  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Page Header */}
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
          commerceStore and unveil the correct UI for the user's current stage
          in the commerce prophecy workflow.
        */}
        <LedgerManager />

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
// --- END OF FILE src/app/ledger/page.tsx ---