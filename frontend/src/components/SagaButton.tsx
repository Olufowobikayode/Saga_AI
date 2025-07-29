'use client';

import { motion } from 'framer-motion';
import React from 'react';

// SAGA UI: Defining the properties (props) our button will accept.
interface SagaButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  className?: string;
  disabled?: boolean; // ADDED: Allow the button to be disabled
}

/**
 * The primary interactive element of the Saga UI.
 * A magnificent, animated button that exudes authority and power.
 */
export default function SagaButton({ children, onClick, className = '', disabled = false }: SagaButtonProps) {
  return (
    <motion.button
      // SAGA UI: Applying the core visual style using Tailwind CSS.
      className={`
        py-3 px-8 rounded-full font-serif font-bold text-lg text-white
        bg-gradient-to-r from-saga-primary to-purple-500
        shadow-lg shadow-saga-primary/30
        hover:brightness-110
        transition-all duration-300
        disabled:opacity-50 disabled:cursor-not-allowed disabled:brightness-75
        ${className}
      `}
      // SAGA UI: Adding fluid animations for a magical feel.
      // The button will gently grow on hover and shrink on click.
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      onClick={onClick}
      disabled={disabled} // PASS THE DISABLED PROP TO THE ACTUAL HTML BUTTON
    >
      {children}
    </motion.button>
  );
}