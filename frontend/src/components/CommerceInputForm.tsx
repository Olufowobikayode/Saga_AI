'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useCommerceStore } from '@/store/commerceStore';
import { useSession } from '@/hooks/useSession';
import InputRune from './InputRune';
import SagaButton from './SagaButton';
import ErrorMessage from './ErrorMessage';

// A simple Select component for this form.
const SelectRune = ({ id, label, name, value, onChange, options }: {
    id: string;
    label: string;
    name: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
    options: string[];
}) => (
    <div>
      <label htmlFor={id} className="block font-serif text-lg text-saga-text-light mb-2">{label}</label>
      <div className="relative">
        <select id={id} name={name} value={value} onChange={onChange} className={`w-full appearance-none bg-saga-bg border-2 border-saga-surface rounded-lg px-4 py-3 text-saga-text-light focus:outline-none focus:ring-2 focus:ring-saga-primary transition-all duration-300`}>
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
 * input fields based on the prophecy the user chose.
 */
export default function CommerceInputForm() {
  const { chosenProphecyType, chosenAuditType, chosenArbitrageMode, forgeProphecy, status, error } = useCommerceStore();
  const isLoading = status === 'forging_prophecy';
  
  const { sessionId, isLoading: isSessionLoading } = useSession();

  const [formData, setFormData] = useState<any>({});
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => {
    if (isSessionLoading || !sessionId) {
      alert("Session is not yet ready. Please wait a moment.");
      return;
    }
    forgeProphecy(formData, sessionId);
  };
  
  const handleRetry = () => {
    handleSubmit();
  };

  const renderFormFields = () => {
    switch (chosenProphecyType) {
      case 'Commerce Audit':
        return (
          <>
            <InputRune id="store_url" name="store_url" label={`Your Store URL (for ${chosenAuditType})`} placeholder="https://your-store.com" type="url" value={formData.store_url || ''} onChange={handleInputChange} optional />
            <InputRune id="statement_text" name="statement_text" label={`Account Statement Text (for ${chosenAuditType})`} as="textarea" placeholder="Paste text from your statements here..." value={formData.statement_text || ''} onChange={handleInputChange} optional />
          </>
        );
      case 'Arbitrage Paths':
        const showProduct = chosenArbitrageMode !== 'Saga_Buys_Saga_Sells';
        const showBuyUrl = chosenArbitrageMode === 'User_Buys_User_Sells' || chosenArbitrageMode === 'User_Buys_Saga_Sells';
        const showSellUrl = chosenArbitrageMode === 'User_Buys_User_Sells' || chosenArbitrageMode === 'Saga_Buys_User_Sells';
        return (
            <>
                {showProduct && <InputRune id="product_name" name="product_name" label="Product Name" placeholder="e.g., 'ergonomic office chair'" value={formData.product_name || ''} onChange={handleInputChange} optional />}
                {showBuyUrl && <InputRune id="buy_from_url" name="buy_from_url" label="Buy From URL" placeholder="e.g., https://www.aliexpress.com/..." type="url" value={formData.buy_from_url || ''} onChange={handleInputChange} optional />}
                {showSellUrl && <InputRune id="sell_on_url" name="sell_on_url" label="Sell On URL" placeholder="e.g., https://www.amazon.com/..." type="url" value={formData.sell_on_url || ''} onChange={handleInputChange} optional />}
                {!showProduct && !showBuyUrl && !showSellUrl && <p className="text-center text-saga-text-dark">Saga has all the information needed to begin her divination.</p>}
            </>
        );
      case 'Social Selling Saga':
        return (
            <>
                <InputRune id="product_name" name="product_name" label="Product Name" placeholder="What artifact will you sell?" value={formData.product_name || ''} onChange={handleInputChange} />
                <InputRune id="social_selling_price" name="social_selling_price" label="Target Selling Price ($)" placeholder="e.g., 29.99" type="text" value={formData.social_selling_price || ''} onChange={handleInputChange} />
                <InputRune id="desired_profit_per_product" name="desired_profit_per_product" label="Desired Profit Per Item ($)" placeholder="e.g., 15.00" type="text" value={formData.desired_profit_per_product || ''} onChange={handleInputChange} />
                <InputRune id="social_platform" name="social_platform" label="Primary Social Platform" placeholder="e.g., TikTok, Instagram" value={formData.social_platform || ''} onChange={handleInputChange} />
                <InputRune id="ads_daily_budget" name="ads_daily_budget" label="Daily Ad Budget ($)" placeholder="e.g., 25.00" type="text" value={formData.ads_daily_budget || ''} onChange={handleInputChange} />
            </>
        );
      case 'Product Route':
        return <SelectRune id="location_type" name="location_type" label="Target Market Scope" value={formData.location_type || 'Global'} onChange={handleInputChange} options={['Global', 'My Location']} />;
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
            <p className="mt-4 text-lg text-saga-text-dark">Provide the final details for the <span className="text-saga-secondary">{chosenProphecyType}</span> prophecy.</p>
        </header>

        <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="space-y-8">
                {renderFormFields()}
                <div className="pt-4 text-center">
                    <SagaButton 
                      onClick={handleSubmit}
                      className="py-3 px-8 text-lg"
                      disabled={isLoading || isSessionLoading}
                    >
                        {isSessionLoading ? "Awaiting Session..." : (isLoading ? "Observing Grand Ritual..." : "Forge Prophecy")}
                    </SagaButton>
                </div>
                
                <ErrorMessage error={error} onRetry={handleRetry} />
            </form>
        </div>
    </motion.div>
  );
}