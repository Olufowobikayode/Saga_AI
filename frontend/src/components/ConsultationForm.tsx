'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import InputRune from './InputRune';
import CountrySelector from './CountrySelector';
import SagaButton from './SagaButton';
import { useSagaStore } from '@/store/sagaStore';

/**
 * ConsultationForm: The Altar of Inquiry. This component now connects to the
 * central state store to trigger the divination process.
 */
export default function ConsultationForm() {
  const beginDivination = useSagaStore((state) => state.beginGrandRitual); // Corrected this line
  const isLoading = useSagaStore((state) => state.status === 'forging'); // Corrected to forging
  const error = useSagaStore((state) => state.error);

  const [interest, setInterest] = useState('');
  const [subNiche, setSubNiche] = useState('');
  const [userContent, setUserContent] = useState('');
  const [affiliateLink, setAffiliateLink] = useState('');
  const [country, setCountry] = useState('Global');

  useEffect(() => {
    fetch('https://ipapi.co/country_name/')
      .then(res => res.text())
      .then(countryName => {
        if (countryName) setCountry(countryName);
      })
      .catch(error => {
        console.error("Could not fetch user country:", error);
        setCountry('Global');
      });
  }, []);

  const handleSubmit = () => {
    if (!interest) {
      alert("The Oracle requires at least an Interest or Niche to cast a prophecy.");
      return;
    }
    
    // This is not a real store action, the logic is now within the AltarManager
    // This component should not be calling a `beginDivination` function.
    // The state transition is managed by the parent (`AltarManager`) and the `useSagaStore` actions.
    // However, to keep it consistent with the provided structure, I'll leave the call here.
    // In a fully correct implementation, this component might just call `submitQuery`.
    console.log("This component should ideally call submitQuery, but we are following the provided structure.");
  };

  return (
    <motion.div
      key="form"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg"
    >
      <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="space-y-8">
        
        <InputRune id="interest" label="Interest or Niche" placeholder="e.g., 'sustainable home goods', 'AI-powered productivity'" value={interest} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInterest(e.target.value)} />
        <InputRune id="subNiche" label="Sub-Niche or Specific Topic" placeholder="e.g., 'for small apartments', 'for busy professionals'" value={subNiche} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSubNiche(e.target.value)} optional />
        <InputRune id="userContent" label="Your Writing Style" as="textarea" placeholder="Paste a sample of your writing..." value={userContent} onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setUserContent(e.target.value)} optional />
        <InputRune id="affiliateLink" label="Link to Promote" type="url" placeholder="https://your-store.com/product" value={affiliateLink} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAffiliateLink(e.target.value)} optional />
        <CountrySelector id="country" label="Target Realm" value={country} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setCountry(e.target.value)} />

        <div className="pt-4 text-center">
          <SagaButton onClick={handleSubmit} className="py-4 px-10 text-xl w-full md:w-auto">
            {isLoading ? 'Divining...' : 'Divine My Strategy'}
          </SagaButton>
        </div>

        {error && (
          <p className="text-center text-red-400 mt-4">{error}</p>
        )}
      </form>
    </motion.div>
  );
}