// --- START OF FILE src/components/AnvilForm.tsx ---
'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useMarketingStore } from '@/store/marketingStore';
import InputRune from './InputRune';
import SagaButton from './SagaButton';

/**
 * AnvilForm: The component where a user provides the core product details
 * to begin the marketing angle prophecy.
 */
export default function AnvilForm() {
  // SAGA LOGIC: Connect to the Mind of the Skald to get the 'commandAnvil' function.
  const commandAnvil = useMarketingStore((state) => state.commandAnvil);
  const isLoading = useMarketingStore((state) => state.status === 'forging_angles');

  // Local state for the form inputs.
  const [productName, setProductName] = useState('');
  const [productDescription, setProductDescription] = useState('');
  const [productLink, setProductLink] = useState('');

  const handleSubmit = () => {
    if (!productName || !productDescription) {
      alert("The Skald requires a Name and Description to begin the forging.");
      return;
    }
    // SAGA LOGIC: Call the command from our store with the form data.
    // This will trigger the state change to 'forging_angles' and begin the ritual.
    commandAnvil(productName, productDescription, productLink);
  };

  return (
    <motion.div
      key="anvil-form"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <form 
        onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} 
        className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg space-y-8"
      >
        <div className="text-center border-b border-saga-primary/20 pb-6 mb-8">
          <h2 className="font-serif text-3xl text-saga-primary">Present Your Artifact</h2>
          <p className="text-saga-text-dark mt-2">Provide the details of the product or service you wish to champion.</p>
        </div>

        <InputRune
          id="productName"
          label="Product or Service Name"
          placeholder="e.g., 'The Chronos Watch', 'AI-Powered Copywriting Service'"
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
        />

        <InputRune
          id="productDescription"
          label="Product Description"
          as="textarea"
          placeholder="Describe its features, benefits, and what makes it unique."
          value={productDescription}
          onChange={(e) => setProductDescription(e.target.value)}
        />

        <InputRune
          id="productLink"
          label="Link"
          type="url"
          placeholder="https://your-product-page.com"
          value={productLink}
          onChange={(e) => setProductLink(e.target.value)}
          optional
        />

        <div className="pt-4 text-center">
          <SagaButton onClick={handleSubmit} className="py-3 px-8 text-lg w-full md:w-auto">
            {isLoading ? "Forging Angles..." : "Forge Marketing Angles"}
          </SagaButton>
        </div>
      </form>
    </motion.div>
  );
}
// --- END OF FILE src/components/AnvilForm.tsx ---