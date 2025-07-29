'use client';

import React from 'react';

// SAGA UI: We define the props using a more advanced TypeScript pattern
// called a "discriminated union" to link the 'as' prop to the correct 'onChange' type.

// 1. Define the props that are common to both inputs and textareas.
type BaseProps = {
  id: string;
  label: string;
  placeholder?: string;
  value: string;
  optional?: boolean;
  className?: string;
};

// 2. Define the props specific to a standard input.
type InputSpecificProps = {
  as?: 'input';
  type?: 'text' | 'url' | 'password';
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

// 3. Define the props specific to a textarea.
type TextareaSpecificProps = {
  as: 'textarea';
  type?: never; // A textarea doesn't have a 'type' attribute like 'url' or 'password'.
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
};

// 4. Combine them: Props must include the base props AND either the input OR textarea props.
type InputRuneProps = BaseProps & (InputSpecificProps | TextareaSpecificProps);

/**
 * InputRune: A themed input component for the Saga UI.
 * It represents the stone tablet upon which a user inscribes their query.
 * This version uses a discriminated union for type-safe props.
 */
export default function InputRune({ className = '', ...props }: InputRuneProps) {
  
  const commonClasses = `
    w-full bg-saga-bg border-2 border-saga-surface rounded-lg
    px-4 py-3 text-saga-text-light placeholder-saga-text-dark
    focus:outline-none focus:ring-2 focus:ring-saga-primary focus:border-transparent
    transition-all duration-300
    disabled:opacity-50
  `;

  return (
    <div className="w-full">
      <label htmlFor={props.id} className="block font-serif text-lg text-saga-text-light mb-2">
        {props.label}
        {props.optional && <span className="text-saga-text-dark text-sm ml-2">(Optional)</span>}
      </label>
      
      {/* Based on the 'as' prop, TypeScript now knows which 'onChange' is valid. */}
      {props.as === 'textarea' ? (
        <textarea
          id={props.id}
          name={props.id}
          placeholder={props.placeholder}
          value={props.value}
          onChange={props.onChange}
          className={`${commonClasses} min-h-[120px] ${className}`}
          rows={4}
        />
      ) : (
        <input
          id={props.id}
          name={props.id}
          type={props.type || 'text'}
          placeholder={props.placeholder}
          value={props.value}
          onChange={props.onChange}
          className={`${commonClasses} ${className}`}
        />
      )}
    </div>
  );
}