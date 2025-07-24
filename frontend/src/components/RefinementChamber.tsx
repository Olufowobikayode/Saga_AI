// --- START OF FILE src/components/RefinementChamber.tsx ---
'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';
import { useVentureStore } from '@/store/ventureStore';
import SagaButton from './SagaButton';

// A reusable, themed dropdown for this form.
const SelectRune = ({ id, label, value, onChange, options }: any) => (
  <div>
    <label htmlFor={id} className="block font-serif text-lg text-saga-text-light mb-2">{label}</label>
    <div className="relative">
      <select
        id={id} value={value} onChange={onChange}
        className={`w-full appearance-none bg-saga-bg border-2 border-saga-surface rounded-lg px-4 py-3 text-saga-text-light focus:outline-none focus:ring-2 focus:ring-saga-primary transition-all duration-300`}
      >
        {options.map((opt: string) => <option key={opt} value={opt}>{opt}</option>)}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-saga-text-dark">
        <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" /></svg>
      </div>
    </div>
  </div>
);

/**
 * RefinementChamber: The new entry form for the Seer's Spire, asking deeper
 * strategic questions to hyper-personalize the prophecy.
 */
export default function RefinementChamber() {
  const { brief } = useSagaStore();
  const { beginQuest, status, error } = useVentureStore();
  const isLoading = status === 'questing_for_visions';

  // State for the new refinement fields
  const [businessModel, setBusinessModel] = useState('Any');
  const [primaryStrength, setPrimaryStrength] = useState('Any');
  const [investmentLevel, setInvestmentLevel] = useState('Any');

  const handleSubmit = () => {
    const ventureBrief = {
      business_model: businessModel,
      primary_strength: primaryStrength,
      investment_level: investmentLevel,
    };
    beginQuest(ventureBrief);
  };

  return (
    <motion.div
      key="refinement-chamber"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
        <header className="text-center border-b border-saga-primary/20 pb-6 mb-8">
          <h2 className="font-serif text-3xl text-saga-primary">The Seer's Refinement</h2>
          <p className="text-saga-text-dark mt-2 max-w-xl mx-auto">
            The Seer acknowledges your quest concerning "<span className="text-saga-text-light font-semibold">{brief.interest}</span>".
            Provide these optional runes of intent to sharpen the focus of the prophecy.
          </p>
        </header>

        <form 
          onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} 
          className="space-y-8"
        >
          <SelectRune
            id="businessModel"
            label="Preferred Business Model"
            value={businessModel}
            onChange={(e) => setBusinessModel(e.target.value)}
            options={['Any', 'Physical Product', 'Digital Service', 'Content & Media', 'Community-Based', 'Low-Cost Dropshipping']}
          />
          <SelectRune
            id="primaryStrength"
            label="Your Primary Strength"
            value={primaryStrength}
            onChange={(e) => setPrimaryStrength(e.target.value)}
            options={['Any', 'I am a Maker/Designer', 'I am a Marketer/Seller', 'I am a Writer/Creator', 'I am a Community Builder']}
          />
          <SelectRune
            id="investmentLevel"
            label="Initial Investment Level"
            value={investmentLevel}
            onChange={(e) => setInvestmentLevel(e.target.value)}
            options={['Any', 'Low (<$500)', 'Medium ($500 - $5,000)', 'High (>$5,000)']}
          />

          <div className="pt-4 text-center">
            <SagaButton onClick={handleSubmit} className="py-3 px-8 text-lg">
              {isLoading ? "Observing Ritual..." : "Begin the Vision Quest"}
            </SagaButton>
          </div>
          {error && <p className="text-center text-red-400 mt-4">{error}</p>}
        </form>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/RefinementChamber.tsx ---