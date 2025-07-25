// --- START OF FILE src/components/LedgerManager.tsx ---
'use client';

import React from 'react';
import { useCommerceStore } from '@/store/commerceStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import CommerceCrossroads from './CommerceCrossroads';
import HallOfScrutiny from './HallOfScrutiny';
import HallOfScales from './HallOfScales'; // Summoning the new Hall of Scales.

// Veils for the components we will soon forge.
const CommerceInputForm = () => <div className="p-8 bg-saga-surface rounded-lg text-center">Awaiting your specific query...</div>;
const CommerceProphecyScroll = () => <div className="p-8 bg-saga-surface rounded-lg text-center">The final prophecy is revealed...</div>;


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
      
      case 'awaiting_audit_type':
        return <HallOfScrutiny />;

      // NEW: Unveil the Hall of Scales at the correct time.
      case 'awaiting_arbitrage_mode':
        return <HallOfScales />;

      case 'awaiting_input':
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
// --- END OF FILE src/components/LedgerManager.tsx ---```