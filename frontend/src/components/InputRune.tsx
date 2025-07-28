'use client';

import React from 'react';

// SAGA UI: Defining the properties for our custom input component.
interface InputRuneProps {
  id: string;
  label: string;
  placeholder?: string; // Placeholder is optional
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  type?: 'text' | 'url' | 'password'; // MODIFIED: Added 'password' as a valid type
  as?: 'input' | 'textarea'; // Allows us to use this component as a single-line or multi-line input
  optional?: boolean; // To display an "(Optional)" hint
  className?: string; // Added className to allow for custom styling
}

/**
 * InputRune: A themed input component for the Saga UI.
 * It represents the stone tablet upon which a user inscribes their query.
 */
export default function InputRune({
  id,
  label,
  placeholder,
  value,
  onChange,
  type = 'text',
  as = 'input',
  optional = false,
  className = '', // Default to an empty string
}: InputRuneProps) {
  
  // Common styling for both input and textarea to ensure consistency.
  const commonClasses = `
    w-full bg-saga-bg border-2 border-saga-surface rounded-lg
    px-4 py-3 text-saga-text-light placeholder-saga-text-dark
    focus:outline-none focus:ring-2 focus:ring-saga-primary focus:border-transparent
    transition-all duration-300
    disabled:opacity-50
  `;

  // Conditionally render either an <input> or a <textarea> element.
  const InputComponent = as === 'textarea' 
    ? <textarea
        id={id}
        name={id}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`${commonClasses} min-h-[120px] ${className}`} // Textareas have a minimum height and pass className
        rows={4}
      />
    : <input
        id={id}
        name={id}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`${commonClasses} ${className}`} // Pass className
      />;

  return (
    <div className="w-full">
      <label htmlFor={id} className="block font-serif text-lg text-saga-text-light mb-2">
        {label}
        {optional && <span className="text-saga-text-dark text-sm ml-2">(Optional)</span>}
      </label>
      {InputComponent}
    </div>
  );
}