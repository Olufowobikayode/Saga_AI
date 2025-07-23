// --- START OF FILE src/components/ConsultationForm.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import InputRune from './InputRune';
import CountrySelector from './CountrySelector';
import SagaButton from './SagaButton';
import { useSagaStore } from '@/store/sagaStore'; // Import the store.

/**
 * ConsultationForm: The Altar of Inquiry. This component now connects to the
 * central state store to trigger the divination process.
 */
export default function ConsultationForm() {
  // SAGA LOGIC: Get the 'beginDivination' function and 'isLoading' status from the store.
  const beginDivination = useSagaStore((state) => state.beginDivination);
  const isLoading = useSagaStore((state) => state.status === 'divining');
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
    
    // SAGA LOGIC: Call the main function from our store with the form data.
    // This will handle setting the loading state, the API call, and the ad timer.
    beginDivination({
      interest: interest,
      // We will add the other fields here as needed by the backend API model.
      // For now, 'interest' is the main one for GrandStrategy.
      target_country_name: country,
      user_content_text: userContent,
      // The backend expects user_content_url, but we can adapt or add it.
      // For now, we'll just send the text.
    });
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
        
        {/* All the InputRune and CountrySelector components remain the same */}
        <InputRune id="interest" label="Interest or Niche" placeholder="e.g., 'sustainable home goods', 'AI-powered productivity'" value={interest} onChange={(e) => setInterest(e.target.value)} />
        <InputRune id="subNiche" label="Sub-Niche or Specific Topic" placeholder="e.g., 'for small apartments', 'for busy professionals'" value={subNiche} onChange={(e) => setSubNiche(e.target.value)} optional />
        <InputRune id="userContent" label="Your Writing Style" as="textarea" placeholder="Paste a sample of your writing..." value={userContent} onChange={(e) => setUserContent(e.target.value)} optional />
        <InputRune id="affiliateLink" label="Link to Promote" type="url" placeholder="https://your-store.com/product" value={affiliateLink} onChange={(e) => setAffiliateLink(e.target.value)} optional />
        <CountrySelector id="country" label="Target Realm" value={country} onChange={(e) => setCountry(e.target.value)} />

        <div className="pt-4 text-center">
          <SagaButton onClick={handleSubmit} className="py-4 px-10 text-xl w-full md:w-auto">
            {isLoading ? 'Divining...' : 'Divine My Strategy'}
          </SagaButton>
        </div>

        {/* SAGA LOGIC: Display an error message if the divination fails. */}
        {error && (
          <p className="text-center text-red-400 mt-4">{error}</p>
        )}
      </form>
    </motion.div>
  );
}
// --- END OF FILE src/components/ConsultationForm.tsx ---