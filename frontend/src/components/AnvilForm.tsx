'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';
import { useSession } from '@/hooks/useSession';
import InputRune from './InputRune';
import SagaButton from './SagaButton';
import ErrorMessage from './ErrorMessage';

export default function AnvilForm() {
  const { commandAnvil, status, error } = useMarketingStore();
  const isLoading = status === 'forging_angles';
  
  const { sessionId, isLoading: isSessionLoading } = useSession();

  const [productName, setProductName] = useState('');
  const [productDescription, setProductDescription] = useState('');
  const [targetAudience, setTargetAudience] = useState('');

  const handleSubmit = () => { /* ... unchanged ... */ };
  const handleRetry = () => { /* ... unchanged ... */ };

  return (
    <motion.div /* ... unchanged ... */ >
      <form 
        onSubmit={(e: React.FormEvent<HTMLFormElement>) => { e.preventDefault(); handleSubmit(); }} 
        className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg space-y-8"
      >
        <div className="text-center border-b border-saga-primary/20 pb-6 mb-8">
          <h2 className="font-serif text-3xl text-saga-primary">Present Your Artifact</h2>
          <p className="text-saga-text-dark mt-2">Provide the details of the product or service you wish to champion.</p>
        </div>

        <InputRune
          id="productName"
          name="productName" // <-- CORRECTED
          label="Product or Service Name"
          placeholder="e.g., 'The Chronos Watch', 'AI-Powered Copywriting Service'"
          value={productName}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setProductName(e.target.value)}
        />

        <InputRune
          id="productDescription"
          name="productDescription" // <-- CORRECTED
          label="Product Description"
          as="textarea"
          placeholder="Describe its features, benefits, and what makes it unique."
          value={productDescription}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setProductDescription(e.target.value)}
        />
        
        <InputRune
          id="targetAudience"
          name="targetAudience" // <-- CORRECTED
          label="Target Audience"
          placeholder="e.g., 'Tech-savvy professionals aged 30-50', 'Eco-conscious millennials'"
          value={targetAudience}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTargetAudience(e.target.value)}
        />

        <div className="pt-4 text-center">
          <SagaButton /* ... */ >
            {isSessionLoading ? "Awaiting Session..." : (isLoading ? "Forging Angles..." : "Forge Marketing Angles")}
          </SagaButton>
        </div>

        <ErrorMessage error={error} onRetry={handleRetry} />
        
      </form>
    </motion.div>
  );
}