// --- START OF FILE src/components/LedgerManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useCommerceStore } from '@/store/commerceStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';

// We will create these new components in the upcoming steps.
// For now, they are placeholders.
const CommerceCrossroads = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for CommerceCrossroads</div>;
const CommerceInputForm = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for CommerceInputForm</div>;
const CommerceProphecyScroll = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for CommerceProphecyScroll</div>;


/**
 * LedgerManager: The master controller for the entire Commerce Saga workflow.
 * It reads the status from the commerceStore and renders the appropriate UI.
 */
export default function LedgerManager() {
  // SAGA LOGIC: Connect to the Mind of the Merchant.
  const status = useCommerceStore((state) => state.status);
  const enterLedger = useCommerceStore((state) => state.enterLedger);

  // SAGA LOGIC: When the manager first appears, it invokes the entry rite.
  useEffect(() => {
    if (status === 'idle') {
      enterLedger();
    }
  }, [status, enterLedger]);

  // This function will decide which component to show.
  const renderCurrentStage = () => {
    switch (status) {
      case 'crossroads':
        return <CommerceCrossroads />;
      
      case 'awaiting_input':
        return <CommerceInputForm />;

      case 'forging_prophecy':
        return <RitualScreen />;

      case 'prophecy_revealed':
        return <CommerceProphecyScroll />;
      
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