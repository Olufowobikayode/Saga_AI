// --- START OF NEW FILE src/components/StrategySidebar.tsx ---
'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSagaStore } from '@/store/sagaStore';

/**
 * StrategySidebar: A collapsible sidebar that displays the core summary of the
 * user's generated Grand Strategy, providing persistent context on tactical pages.
 */
export default function StrategySidebar() {
  const [isOpen, setIsOpen] = useState(false);
  
  // Read the strategy data directly from the main sagaStore
  const strategyData = useSagaStore((state) => state.strategyData);

  // If there's no strategy data yet, don't render anything.
  if (!strategyData || !strategyData.prophecy) {
    return null;
  }

  const { prophecy_title, divine_summary } = strategyData.prophecy;

  const sidebarVariants = {
    open: {
      x: 0,
      transition: { type: 'spring', stiffness: 200, damping: 25 },
    },
    closed: {
      x: '100%',
      transition: { type: 'spring', stiffness: 200, damping: 25 },
    },
  };

  const buttonVariants = {
    open: {
      rotate: 0,
    },
    closed: {
      rotate: 180,
    },
  };

  return (
    <>
      {/* The floating button to open/close the sidebar */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-1/3 right-0 z-40 bg-saga-secondary p-3 rounded-l-full shadow-lg"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        <motion.div
          animate={isOpen ? 'closed' : 'open'}
          variants={buttonVariants}
          transition={{ duration: 0.3 }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-saga-bg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </motion.div>
      </motion.button>
      
      <AnimatePresence>
        {isOpen && (
          <>
            {/* The main sidebar panel */}
            <motion.div
              variants={sidebarVariants}
              initial="closed"
              animate="open"
              exit="closed"
              className="fixed top-0 right-0 h-full w-full max-w-md bg-saga-surface border-l-2 border-saga-primary z-30 p-8 shadow-2xl overflow-y-auto"
            >
              <h2 className="font-serif text-3xl font-bold text-saga-secondary mb-2">
                Grand Strategy
              </h2>
              <h3 className="font-semibold text-xl text-saga-text-light mb-6">
                {prophecy_title}
              </h3>

              <div className="border-t border-white/10 pt-6">
                <h4 className="font-serif text-2xl text-saga-primary mb-3">
                  Divine Summary
                </h4>
                <p className="text-saga-text-dark leading-relaxed whitespace-pre-wrap">
                  {divine_summary}
                </p>
              </div>

              {/* You could add more sections here in the future, like the "Target Soul Profile" */}

            </motion.div>

            {/* A backdrop to dim the main content when the sidebar is open */}
            <motion.div
              onClick={() => setIsOpen(false)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 z-20"
            />
          </>
        )}
      </AnimatePresence>
    </>
  );
}
// --- END OF NEW FILE src/components/StrategySidebar.tsx ---