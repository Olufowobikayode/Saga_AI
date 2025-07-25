// --- START OF FILE src/components/LedgerManager.tsx ---
'use client';

import React from 'react';
import { useCommerceStore } from '@/store/commerceStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import CommerceCrossroads from './CommerceCrossroads';
import CommerceInputForm from './CommerceInputForm';
import CommerceProphecyScroll from './CommerceProphecyScroll'; // Summoning the real Final Scroll.

/**
 * LedgerManager: The master controller for the entire Commerce Saga workflow.
 * It reads the status from the commerceStore and renders the appropriate UI.
 */
export default function LedgerManager() {
  const status = useCommerceStore((state) => state.status);

  // This function decides which sacred chamber to unveil.
  const renderCurrentStage = () => {
    switch (status) {
      case 'crossroads':
        return <CommerceCrossroads />;
      
      case 'awaiting_input':
        return <CommerceInputForm />;

      case 'prophecy_revealed':
        // Now unveiling the real component instead of the veil.
        return <CommerceProphecyScroll />;

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