// --- START OF FILE src/components/ScrollUnfurled.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';

// SAGA LOGIC: Defining the properties for this component.
interface ScrollUnfurledProps {
  title: string;
  content: string | object; // Can handle simple text or structured objects.
  onBack: () => void; // A function to return to the previous screen.
}

/**
 * ScrollUnfurled: A focused view to display a single, detailed piece of a prophecy,
 * such as generated code or a deployment guide.
 */
export default function ScrollUnfurled({ title, content, onBack }: ScrollUnfurledProps) {

  const handleCopy = () => {
    const textToCopy = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
    navigator.clipboard.writeText(textToCopy);
  };
  
  const renderContent = () => {
    // For HTML code
    if (title.toLowerCase().includes('html')) {
      return (
        <pre className="text-saga-text-dark whitespace-pre-wrap font-mono bg-saga-bg p-4 rounded-md text-sm overflow-x-auto">
          <code>{content as string}</code>
        </pre>
      );
    }
    // For structured guides
    if (typeof content === 'object' && content !== null) {
      return (
        <ul className="space-y-4 text-lg">
          {Object.entries(content).map(([key, value]) => (
            <li key={key} className="text-saga-text-dark leading-relaxed">
              <strong className="block text-saga-primary font-serif mb-1">{key}:</strong>
              <span>{Array.isArray(value) ? value.join(', ') : String(value)}</span>
            </li>
          ))}
        </ul>
      );
    }
    // Default for plain text
    return <p className="text-saga-text-dark whitespace-pre-wrap font-sans text-lg">{content as string}</p>;
  };

  return (
    <motion.div
      key="scroll-unfurled"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="bg-saga-surface p-6 md:p-8 rounded-lg border border-white/10">
        <div className="flex justify-between items-center mb-6 border-b border-white/10 pb-4">
          <h2 className="font-serif text-3xl font-bold text-saga-secondary">{title}</h2>
          <button 
            onClick={handleCopy}
            className="bg-saga-bg text-saga-primary px-4 py-2 rounded-md hover:bg-saga-primary hover:text-white transition-colors"
          >
            Copy Content
          </button>
        </div>
        
        <div className="prose prose-invert max-w-none">
          {renderContent()}
        </div>
      </div>

      {/* Back Button to return to the Final Scroll */}
      <div className="text-center mt-16">
        <button 
          onClick={onBack}
          className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors"
        >
          ← Return to the Final Scroll
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/ScrollUnfurled.tsx ---