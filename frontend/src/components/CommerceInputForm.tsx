// --- START OF FILE src/components/CommerceInputForm.tsx ---
'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useCommerceStore } from '@/store/commerceStore';
import InputRune from './InputRune';
import SagaButton from './SagaButton';

// A simple Select component for this form.
const SelectRune = ({ id, label, value, onChange, options }: any) => (
    <div>
      <label htmlFor={id} className="block font-serif text-lg text-saga-text-light mb-2">{label}</label>
      <div className="relative">
        <select id={id} value={value} onChange={onChange} className={`w-full appearance-none bg-saga-bg border-2 border-saga-surface rounded-lg px-4 py-3 text-saga-text-light focus:outline-none focus:ring-2 focus:ring-saga-primary transition-all duration-300`}>
          {options.map((opt: string) => <option key={opt} value={opt}>{opt}</option>)}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-saga-text-dark">
          <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" /></svg>
        </div>
      </div>
    </div>
);


/**
 * CommerceInputForm: An intelligent form that dynamically displays the correct
 * input fields based on the prophecy the user chose at the Crossroads.
 */
export default function CommerceInputForm() {
  const { chosenProphecyType, forgeProphecy, status, error } = useCommerceStore();
  const isLoading = status === 'forging_prophecy';

  // State for ALL possible form fields.
  const [formData, setFormData] = useState<any>({});
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => {
    // Basic validation can be added here if needed.
    forgeProphecy(formData);
  };
  
  // SAGA LOGIC: This function renders the correct form fields.
  const renderFormFields = () => {
    switch (chosenProphecyType) {
      case 'Commerce Audit':
        return (
          <>
            <SelectRune id="audit_type" label="Type of Audit" value={formData.audit_type || 'Store Audit'} onChange={handleInputChange} options={['Store Audit', 'Account Audit', 'Account Prediction']} />
            <InputRune id="store_url" label="Your Store URL" placeholder="https://your-store.com" type="url" value={formData.store_url || ''} onChange={handleInputChange} optional />
            <InputRune id="statement_text" label="Account Statement Text" as="textarea" placeholder="Paste text from your TXT or CSV statements here..." value={formData.statement_text || ''} onChange={handleInputChange} optional />
          </>
        );
      case 'Arbitrage Paths':
        return (
            <>
                <SelectRune id="mode" label="Arbitrage Mode" value={formData.mode || 'Saga_Buys_Saga_Sells'} onChange={handleInputChange} options={["User_Buys_User_Sells", "Saga_Buys_User_Sells", "User_Buys_Saga_Sells", "Saga_Buys_Saga_Sells"]} />
                <InputRune id="product_name" label="Product Name" placeholder="e.g., 'ergonomic office chair'" value={formData.product_name || ''} onChange={handleInputChange} optional />
                <InputRune id="buy_from_url" label="Buy From URL" placeholder="e.g., https://www.aliexpress.com/..." type="url" value={formData.buy_from_url || ''} onChange={handleInputChange} optional />
                <InputRune id="sell_on_url" label="Sell On URL" placeholder="e.g., https://www.amazon.com/..." type="url" value={formData.sell_on_url || ''} onChange={handleInputChange} optional />
            </>
        );
      case 'Social Selling Saga':
        return (
            <>
                <InputRune id="product_name" label="Product Name" placeholder="What artifact will you sell?" value={formData.product_name || ''} onChange={handleInputChange} />
                <InputRune id="social_selling_price" label="Target Selling Price ($)" placeholder="e.g., 29.99" type="text" value={formData.social_selling_price || ''} onChange={handleInputChange} />
                <InputRune id="desired_profit_per_product" label="Desired Profit Per Item ($)" placeholder="e.g., 15.00" type="text" value={formData.desired_profit_per_product || ''} onChange={handleInputChange} />
                <InputRune id="social_platform" label="Primary Social Platform" placeholder="e.g., TikTok, Instagram" value={formData.social_platform || ''} onChange={handleInputChange} />
            </>
        );
      case 'Product Route':
        return <SelectRune id="location_type" label="Target Market Scope" value={formData.location_type || 'Global'} onChange={handleInputChange} options={['Global', 'My Location']} />;
      default:
        return <p>The prophecy type is unknown. Please return to the Crossroads.</p>;
    }
  };

  return (
    <motion.div
      key="commerce-input-form"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
        <header className="text-center mb-12">
            <h2 className="font-serif text-4xl font-bold text-white">Inscribe Your Query</h2>
            <p className="mt-4 text-lg text-saga-text-dark">Provide the details for the <span className="text-saga-secondary">{chosenProphecyType}</span> prophecy.</p>
        </header>

        <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="space-y-8">
                {renderFormFields()}
                <div className="pt-4 text-center">
                    <SagaButton onClick={handleSubmit} className="py-3 px-8 text-lg">
                        {isLoading ? "Observing Ritual..." : "Forge Prophecy"}
                    </SagaButton>
                </div>
                {error && <p className="text-center text-red-400 mt-4">{error}</p>}
            </form>
        </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/CommerceInputForm.tsx ---