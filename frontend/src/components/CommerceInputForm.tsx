'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useCommerceStore } from '@/store/commerceStore';
import { useSession } from '@/hooks/useSession';
import InputRune from './InputRune';
import SagaButton from './SagaButton';
import ErrorMessage from './ErrorMessage';

// The SelectRune component is unchanged
const SelectRune = (/* ... */) => ( /* ... */ );

export default function CommerceInputForm() {
  const { chosenProphecyType, chosenAuditType, chosenArbitrageMode, forgeProphecy, status, error } = useCommerceStore();
  const isLoading = status === 'forging_prophecy';
  
  const { sessionId, isLoading: isSessionLoading } = useSession();

  const [formData, setFormData] = useState<any>({});
  
  // CORRECTED: This handler is now fully type-safe
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => { /* ... unchanged ... */ };
  const handleRetry = () => { /* ... unchanged ... */ };

  const renderFormFields = () => {
    switch (chosenProphecyType) {
      case 'Commerce Audit':
        return (
          <>
            <InputRune id="store_url" name="store_url" label={`Your Store URL (for ${chosenAuditType})`} placeholder="https://your-store.com" type="url" value={formData.store_url || ''} onChange={handleInputChange} optional />
            <InputRune id="statement_text" name="statement_text" label={`Account Statement Text (for ${chosenAuditType})`} as="textarea" placeholder="Paste text from your statements here..." value={formData.statement_text || ''} onChange={handleInputChange} optional />
          </>
        );
        // ... other cases are unchanged as they use the now-correct InputRune
      default:
        return <p>The prophecy type is unknown. Please return to the Crossroads.</p>;
    }
  };

  return (
    <motion.div /* ... unchanged ... */ >
        <header /* ... unchanged ... */ ></header>
        <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="space-y-8">
                {renderFormFields()}
                <div className="pt-4 text-center">
                    <SagaButton /* ... */ >
                        {isSessionLoading ? "Awaiting Session..." : (isLoading ? "Observing Grand Ritual..." : "Forge Prophecy")}
                    </SagaButton>
                </div>
                <ErrorMessage error={error} onRetry={handleRetry} />
            </form>
        </div>
    </motion.div>
  );
}