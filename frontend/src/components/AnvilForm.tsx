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
  const commandAnvil = useMarketingStore((state) => state.commandAnvil);
  const isLoading = useMarketingStore((state) => state.status === 'forging_angles');
  const error = useMarketingStore((state) => state.error);

  const [productName, setProductName] = useState('');
  const [productDescription, setProductDescription] = useState('');
  const [targetAudience, setTargetAudience] = useState(''); // NEW field
  // The productLink is not required by the angles API, so we can remove it for this specific form if desired,
  // but we'll keep it for potential future use.
  const [productLink, setProductLink] = useState('');

  const handleSubmit = () => {
    if (!productName || !productDescription || !targetAudience) {
      alert("The Skald requires a Name, Description, and Target Audience to begin the forging.");
      return;
    }
    // Call the command from our store with all required data.
    commandAnvil(productName, productDescription, targetAudience);
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

        {/* NEW: Target Audience field, required by the backend. */}
        <InputRune
          id="targetAudience"
          label="Target Audience"
          placeholder="e.g., 'Tech-savvy professionals aged 30-50', 'Eco-conscious millennials'"
          value={targetAudience}
          onChange={(e) => setTargetAudience(e.target.value)}
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

        {/* Display any errors that occur during the API call */}
        {error && (
          <p className="text-center text-red-400 mt-4">{error}</p>
        )}
      </form>
    </motion.div>
  );
}
// --- END OF FILE src/components/AnvilForm.tsx ---