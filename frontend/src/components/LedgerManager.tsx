// --- START OF FILE src/components/LedgerManager.tsx ---
'use client';

import React from 'react';
import { useCommerceStore } from '@/store/commerceStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import CommerceCrossroads from './CommerceCrossroads';
import HallOfScrutiny from './HallOfScrutiny';
import HallOfScales from './HallOfScales';
import CommerceInputForm from './CommerceInputForm'; // Summoning the real, intelligent Input Form.

// Veil for the final component we will forge.
const CommerceProphecyScroll = () => <div className="p-8 bg-saga-surface rounded-lg text-center">The final prophecy is revealed...</div>;


/**
 * LedgerManager: The master controller for the entire Commerce Saga workflow.
 * It reads the status from the commerceStore and renders the appropriate UI.
 */
export default function LedgerManager() {
  const status = useCommerceStore((state) => state.status);

  const renderCurrentStage = () => {
    switch (status) {
      case 'crossroads':
        return <CommerceCrossroads />;
      
      case 'awaiting_audit_type':
        return <HallOfScrutiny />;

      case 'awaiting_arbitrage_mode':
        return <HallOfScales />;

      case 'awaiting_input':
        // Now unveiling the real component instead of the veil.
        return <CommerceInputForm />;

      case 'prophecy_revealed':
        return <CommerceProphecyScroll />;

      case 'performing_entry_rite':
      case 'performing_choice_rite':
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