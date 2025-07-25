// --- START OF FILE frontend/src/components/LedgerManager.tsx ---
'use client';

import React from 'react';
import { useCommerceStore } from '@/store/commerceStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import CommerceCrossroads from './CommerceCrossroads';
import HallOfScrutiny from './HallOfScrutiny';
import HallOfScales from './HallOfScales';
import CommerceInputForm from './CommerceInputForm';
import CommerceProphecyScroll from './CommerceProphecyScroll';

/**
 * LedgerManager: The master controller for the entire Commerce Saga workflow.
 * It reads the status from the commerceStore and renders the appropriate UI.
 */
export default function LedgerManager() {
  const status = useCommerceStore((state) => state.status);
  const ritualPromise = useCommerceStore((state) => state.ritualPromise);

  const handleRitualComplete = () => {
    console.log("LedgerManager acknowledges ritual completion.");
    // The store manages its own state transitions upon promise resolution.
  };

  // This function decides which sacred chamber to unveil.
  const renderCurrentStage = () => {
    switch (status) {
      case 'crossroads':
        return <CommerceCrossroads />;
      
      case 'awaiting_audit_type':
        return <HallOfScrutiny />;

      case 'awaiting_arbitrage_mode':
        return <HallOfScales />;

      case 'awaiting_input':
        return <CommerceInputForm />;

      case 'prophecy_revealed':
        return <CommerceProphecyScroll />;

      case 'performing_entry_rite':
      case 'performing_choice_rite':
      case 'forging_prophecy':
        // CORRECTED: Pass the required props to RitualScreen
        return (
          <RitualScreen
            key={`ledger-ritual-${status}`}
            ritualPromise={ritualPromise}
            onRitualComplete={handleRitualComplete}
          />
        );
      
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
// --- END OF FILE frontend/src/components/LedgerManager.tsx ---