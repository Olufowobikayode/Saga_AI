// --- START OF FILE src/components/RealmForm.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';
import CountrySelector from './CountrySelector';
import SagaButton from './SagaButton';

/**
 * RealmForm: The third and final stage of the Grand Ritual. Captures the
 * user's geographic targeting choice.
 */
export default function RealmForm() {
  const submitRealmAndDivine = useSagaStore((state) => state.submitRealmAndDivine);
  const isLoading = useSagaStore((state) => state.status === 'performing_grand_rite');

  const [country, setCountry] = useState('Global');

  // SAGA LOGIC: Pre-fill the country from the IP detection.
  useEffect(() => {
    fetch('https://ipapi.co/country_name/')
      .then(res => res.text())
      .then(countryName => {
        if (countryName) {
          setCountry(countryName);
        }
      })
      .catch(error => {
        console.error("Could not fetch user country:", error);
        setCountry('Global');
      });
  }, []);

  const handleSubmit = () => {
    // Call the final rite from the store with the chosen country.
    // This will trigger the Grand Ritual and the final API call.
    submitRealmAndDivine(country);
  };

  return (
    <motion.div
      key="realm-form"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
          The Realm of Prophecy
        </h1>
        <p className="mt-4 text-xl text-saga-text-dark">
          Step 3 of 3: Select the realm for which your strategy shall be forged.
        </p>
      </header>

      <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} 
          className="space-y-8"
        >
          <CountrySelector
            id="country"
            label="Target Realm"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          />

          <div className="pt-4 text-center">
            <SagaButton onClick={handleSubmit} className="py-4 px-10 text-xl">
              {isLoading ? "Observing Grand Ritual..." : "Divine My Grand Strategy"}
            </SagaButton>
          </div>
        </form>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/RealmForm.tsx ---