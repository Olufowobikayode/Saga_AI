// --- START OF FILE src/components/SagaButton.tsx ---
'use client'; // This directive marks this as a Client Component, allowing for interactivity (like onClick).

import { motion } from 'framer-motion';
import React from 'react';

// SAGA UI: Defining the properties (props) our button will accept.
// It can receive children (like text), an onClick function, and optional custom styling.
interface SagaButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  className?: string;
}

/**
 * The primary interactive element of the Saga UI.
 * A magnificent, animated button that exudes authority and power.
 */
export default function SagaButton({ children, onClick, className = '' }: SagaButtonProps) {
  return (
    <motion.button
      // SAGA UI: Applying the core visual style using Tailwind CSS.
      // This creates a large, rounded, gradient button with a serif font and a subtle glow.
      className={`
        py-3 px-8 rounded-full font-serif font-bold text-lg text-white
        bg-gradient-to-r from-saga-primary to-purple-500
        shadow-lg shadow-saga-primary/30
        hover:brightness-110
        transition-all duration-300
        ${className}
      `}
      // SAGA UI: Adding fluid animations for a magical feel.
      // The button will gently grow on hover and shrink on click.
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      onClick={onClick}
    >
      {children}
    </motion.button>
  );
}
// --- END OF FILE src/components/SagaButton.tsx ---