// --- START OF FILE src/components/ConsultationForm.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import InputRune from './InputRune';
import CountrySelector from './CountrySelector';
import SagaButton from './SagaButton';

/**
 * ConsultationForm: The Altar of Inquiry. This component handles all user inputs
 * for the main strategic prophecy.
 */
export default function ConsultationForm() {
  // SAGA LOGIC: State management for all form fields.
  const [interest, setInterest] = useState('');
  const [subNiche, setSubNiche] = useState('');
  const [userContent, setUserContent] = useState('');
  const [affiliateLink, setAffiliateLink] = useState('');
  const [country, setCountry] = useState('Global');
  const [isLoading, setIsLoading] = useState(false);

  // SAGA LOGIC: This effect runs once on component load to detect the user's country.
  // This fulfills the requirement to pre-select the country based on IP.
  useEffect(() => {
    // We use a free, privacy-friendly service to get the country.
    fetch('https://ipapi.co/country_name/')
      .then(res => res.text())
      .then(countryName => {
        if (countryName) {
          setCountry(countryName);
        }
      })
      .catch(error => {
        console.error("Could not fetch user country:", error);
        // If it fails, we gracefully fall back to 'Global'.
        setCountry('Global');
      });
  }, []); // The empty array [] ensures this runs only once.

  // SAGA LOGIC: This function will be called when the user submits the form.
  const handleSubmit = () => {
    if (!interest) {
      alert("The Oracle requires at least an Interest or Niche to cast a prophecy.");
      return;
    }
    setIsLoading(true);
    console.log("Form submitted! Preparing the ritual...");
    console.log({
      interest,
      subNiche,
      userContent,
      affiliateLink,
      country,
    });
    // In the future, this is where we will call the backend API,
    // start the 30-second ad timer, and navigate to the loading screen.
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg"
    >
      <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="space-y-8">
        
        {/* 1. Interest or Niche (Primary Input) */}
        <InputRune
          id="interest"
          label="Interest or Niche"
          placeholder="e.g., 'sustainable home goods', 'AI-powered productivity', 'handmade leather crafts'"
          value={interest}
          onChange={(e) => setInterest(e.target.value)}
        />

        {/* 2. Optional Sub-Niche */}
        <InputRune
          id="subNiche"
          label="Sub-Niche or Specific Topic"
          placeholder="e.g., 'for small apartments', 'for busy professionals', 'wallets and belts'"
          value={subNiche}
          onChange={(e) => setSubNiche(e.target.value)}
          optional
        />

        {/* 3. Optional User Content for Tone Analysis */}
        <InputRune
          id="userContent"
          label="Your Writing Style"
          as="textarea"
          placeholder="Paste a sample of your writing (e.g., from a blog post or email) so Saga can adopt your voice."
          value={userContent}
          onChange={(e) => setUserContent(e.target.value)}
          optional
        />

        {/* 4. Optional Link for Promotion */}
        <InputRune
          id="affiliateLink"
          label="Link to Promote"
          type="url"
          placeholder="https://your-store.com/product or https://your-youtube-channel.com"
          value={affiliateLink}
          onChange={(e) => setAffiliateLink(e.target.value)}
          optional
        />

        {/* 5. Country Selector */}
        <CountrySelector
          id="country"
          label="Target Realm"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
        />

        {/* 6. Submission Button */}
        <div className="pt-4 text-center">
          <SagaButton onClick={handleSubmit} className="py-4 px-10 text-xl w-full md:w-auto">
            Divine My Strategy
          </SagaButton>
        </div>

      </form>
    </motion.div>
  );
}
// --- END OF FILE src/components/ConsultationForm.tsx ---