// --- START OF FILE src/components/LedgerManager.tsx ---
'use client';

import React from 'react';
import { useCommerceStore } from '@/store/commerceStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';

// Veils for the components we will soon forge.
const CommerceCrossroads = () => <div className="p-8 bg-saga-surface rounded-lg text-center">Awaiting choice of prophecy...</div>;
const CommerceInputForm = () => <div className="p-8 bg-saga-surface rounded-lg text-center">Awaiting your specific query...</div>;
const CommerceProphecyScroll = () => <div className="p-8 bg-saga-surface rounded-lg text-center">The final prophecy is revealed...</div>;


/**
 * LedgerManager: The master controller for the entire Commerce Saga workflow.
 * It reads the status from the commerceStore and renders the appropriate UI.
 */
export default function LedgerManager() {
  // SAGA LOGIC: Connect to the Mind of the Merchant.
  const status = useCommerceStore((state) => state.status);

  // This function decides which sacred chamber to unveil.
  const renderCurrentStage = () => {
    switch (status) {
      case 'crossroads':
        return <CommerceCrossroads />;
      
      case 'awaiting_input':
        return <CommerceInputForm />;

      case 'prophecy_revealed':
        return <CommerceProphecyScroll />;

      // The RitualScreen is now shown for ALL forging states, including the entry rite
      // and the choice rite, as you commanded.
      case 'performing_entry_rite':
      case 'forging_prophecy':
        return <RitualScreen />;
      
      default:
        return <div className="text-center p-8">Opening the Merchant's Ledger...</div>;
    }
  };

  return (
    <div>
      <AnimatePresence mode="wait">
        {renderCurrentStage()}
      </AnimatePresence>
    </div>
  );
}
// --- END OF FILE src/components/LedgerManager.tsx ---