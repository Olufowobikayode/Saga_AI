'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';
import { useSession } from '@/hooks/useSession';
import CountrySelector from './CountrySelector';
import SagaButton from './SagaButton';

/**
 * RealmForm: The third and final stage of the Grand Ritual. Captures the
 * user's geographic targeting choice.
 */
export default function RealmForm() {
  const submitRealmAndDivine = useSagaStore((state) => state.submitRealmAndDivine);
  const status = useSagaStore((state) => state.status);
  const isLoading = status === 'forging';

  const [country, setCountry] = useState('Global');
  
  const { sessionId, isLoading: isSessionLoading } = useSession();

  // SAGA LOGIC: Pre-fill the country from the IP detection.
  useEffect(() => {
    // Fetches location from a free geo IP service to provide a smart default
    fetch('/api/v10/get-my-location')
      .then(res => {
        if (res.ok) {
          return res.json();
        }
        throw new Error('Could not fetch location');
      })
      .then(data => {
        // We expect a format like "City, Country"
        const countryName = data.location?.split(', ')[1];
        if (countryName && countryName.trim().length > 0) {
          setCountry(countryName);
        }
      })
      .catch(error => {
        console.error("Could not fetch user country via backend:", error);
        // Fallback or just keep the default 'Global'
        setCountry('Global');
      });
  }, []);

  const handleSubmit = () => {
    if (isSessionLoading) {
      alert("Session is still materializing. Please wait a moment.");
      return;
    }

    if (!sessionId) {
      alert("A valid session is required to forge a prophecy. Please refresh the page.");
      return;
    }
    
    submitRealmAndDivine(country, sessionId);
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
            <SagaButton 
              onClick={handleSubmit} 
              className="py-4 px-10 text-xl"
              disabled={isLoading || isSessionLoading} // Using the new 'disabled' prop
            >
              {isSessionLoading ? "Awaiting Session..." : (isLoading ? "Observing Grand Ritual..." : "Divine My Grand Strategy")}
            </SagaButton>
          </div>
        </form>
      </div>
    </motion.div>
  );
}