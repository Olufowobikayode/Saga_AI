'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';
import InputRune from './InputRune';
import SagaButton from './SagaButton';
import { assetTypes, linkTypes } from '@/lib/assetTypes';

// A simple, reusable dropdown component for this form.
const SelectRune = ({ id, name, label, value, onChange, options, optional = false }: {
  id: string;
  name: string;
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: string[];
  optional?: boolean;
}) => (
  <div>
    <label htmlFor={id} className="block font-serif text-lg text-saga-text-light mb-2">
      {label}
      {optional && <span className="text-saga-text-dark text-sm ml-2">(Optional)</span>}
    </label>
    <div className="relative">
      <select
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        className={`w-full appearance-none bg-saga-bg border-2 border-saga-surface rounded-lg px-4 py-3 text-saga-text-light focus:outline-none focus:ring-2 focus:ring-saga-primary transition-all duration-300`}
      >
        <option value="">Select an option...</option>
        {options.map((opt: string) => <option key={opt} value={opt}>{opt}</option>)}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-saga-text-dark">
        <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" /></svg>
      </div>
    </div>
  </div>
);

/**
 * ArtifactForm: The second stage of the Grand Ritual. Captures details about
 * the user's specific asset or link to promote.
 */
export default function ArtifactForm() {
  const submitArtifact = useSagaStore((state) => state.submitArtifact);
  const isLoading = useSagaStore((state) => state.status === 'forging');

  const [assetType, setAssetType] = useState('');
  const [assetName, setAssetName] = useState('');
  const [assetDescription, setAssetDescription] = useState('');
  const [promoLinkType, setPromoLinkType] = useState('');
  const [promoLinkUrl, setPromoLinkUrl] = useState('');
  
  const handleSubmit = () => {
    submitArtifact(assetType, assetName, assetDescription, promoLinkType, promoLinkUrl);
  };

  return (
    <motion.div
      key="artifact-form"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
          The Artifact's Declaration
        </h1>
        <p className="mt-4 text-xl text-saga-text-dark">
          Step 2 of 3: Declare the asset you wish to champion. (All fields are optional)
        </p>
      </header>

      <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
        <form 
          onSubmit={(e: React.FormEvent<HTMLFormElement>) => { e.preventDefault(); handleSubmit(); }} 
          className="space-y-8"
        >
          <SelectRune id="assetType" name="assetType" label="Type of Asset" value={assetType} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setAssetType(e.target.value)} options={assetTypes} optional />
          <InputRune id="assetName" name="assetName" label="Name of Asset" placeholder="e.g., 'The Chronos Watch', 'Saga Community'" value={assetName} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAssetName(e.target.value)} optional />
          <InputRune id="assetDescription" name="assetDescription" label="Description of Asset" as="textarea" placeholder="Describe your product, service, community, or website..." value={assetDescription} onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setAssetDescription(e.target.value)} optional />
          
          <div className="border-t border-saga-primary/20 pt-8 space-y-8">
            <SelectRune id="promoLinkType" name="promoLinkType" label="Type of Link" value={promoLinkType} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setPromoLinkType(e.target.value)} options={linkTypes} optional />
            <InputRune id="promoLinkUrl" name="promoLinkUrl" label="Promotional Link" type="url" placeholder="https://your-link.com" value={promoLinkUrl} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPromoLinkUrl(e.target.value)} optional />
          </div>

          <div className="pt-4 text-center">
            <SagaButton onClick={handleSubmit} className="py-3 px-8 text-lg" disabled={isLoading}>
              {isLoading ? "Observing Ritual..." : "Next: Select Realm"}
            </SagaButton>
          </div>
        </form>
      </div>
    </motion.div>
  );
}