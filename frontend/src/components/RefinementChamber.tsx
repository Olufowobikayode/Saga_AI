'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useVentureStore } from '@/store/ventureStore';
import { useSagaStore } from '@/store/sagaStore';
import { useSession } from '@/hooks/useSession';
import SagaButton from './SagaButton';
import ErrorMessage from './ErrorMessage';
import { businessModels, primaryStrengths, investmentLevels } from '@/lib/ventureOptions';

// A reusable Select component for this form.
const SelectRune = ({ id, label, value, onChange, options }: { 
  id: string;
  label: string; 
  value: string; 
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void; 
  options: string[];
}) => (
  <div>
    <label htmlFor={id} className="block font-serif text-lg text-saga-text-light mb-2">{label}</label>
    <div className="relative">
      <select id={id} name={id} value={value} onChange={onChange} className={`w-full appearance-none bg-saga-bg border-2 border-saga-surface rounded-lg px-4 py-3 text-saga-text-light focus:outline-none focus:ring-2 focus:ring-saga-primary transition-all duration-300`}>
        {options.map((opt: string) => <option key={opt} value={opt}>{opt}</option>)}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-saga-text-dark">
        <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" /></svg>
      </div>
    </div>
  </div>
);

/**
 * RefinementChamber: The form where a user refines their new venture query
 * with personal context before the Vision Quest begins.
 */
export default function RefinementChamber() {
  const { beginQuest, status, error } = useVentureStore();
  const isLoading = status === 'questing_for_visions';
  const interest = useSagaStore((state) => state.brief.interest);
  
  const { sessionId, isLoading: isSessionLoading } = useSession();

  const [brief, setBrief] = useState({
    business_model: businessModels[0],
    primary_strength: primaryStrengths[0],
    investment_level: investmentLevels[0],
  });

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setBrief({ ...brief, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => {
    if (isSessionLoading || !sessionId) {
      alert("Session is not yet ready. Please wait a moment.");
      return;
    }
    beginQuest(brief, sessionId);
  };

  const handleRetry = () => {
    handleSubmit();
  };

  return (
    <motion.div
      key="refinement-chamber"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl font-bold text-white">
          Refine Your Vision Quest
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Provide your strategic preferences for the interest of "<span className="text-saga-secondary">{interest}</span>".
        </p>
      </header>
      
      <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
        <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="space-y-8">
            <SelectRune id="business_model" label="Preferred Business Model" value={brief.business_model} onChange={handleSelectChange} options={businessModels} />
            <SelectRune id="primary_strength" label="Your Primary Strength" value={brief.primary_strength} onChange={handleSelectChange} options={primaryStrengths} />
            <SelectRune id="investment_level" label="Preferred Investment Level" value={brief.investment_level} onChange={handleSelectChange} options={investmentLevels} />

            <div className="pt-4 text-center">
                <SagaButton 
                  onClick={handleSubmit} 
                  className="py-3 px-8 text-lg"
                  disabled={isLoading || isSessionLoading}
                >
                    {isSessionLoading ? "Awaiting Session..." : (isLoading ? "Observing Ritual..." : "Begin the Vision Quest")}
                </SagaButton>
            </div>
            
            <ErrorMessage error={error} onRetry={handleRetry} />
        </form>
      </div>
    </motion.div>
  );
}