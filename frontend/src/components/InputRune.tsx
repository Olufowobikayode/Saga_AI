'use client';

import React from 'react';

type BaseProps = {
  id: string;
  name: string; // The required 'name' prop
  label: string;
  placeholder?: string;
  value: string;
  optional?: boolean;
  className?: string;
};

type InputSpecificProps = {
  as?: 'input';
  type?: 'text' | 'url' | 'password';
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

type TextareaSpecificProps = {
  as: 'textarea';
  type?: never;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
};

type InputRuneProps = BaseProps & (InputSpecificProps | TextareaSpecificProps);

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
      
      {props.as === 'textarea' ? (
        <textarea
          id={props.id}
          name={props.name}
          placeholder={props.placeholder}
          value={props.value}
          onChange={props.onChange}
          className={`${commonClasses} min-h-[120px] ${className}`}
          rows={4}
        />
      ) : (
        <input
          id={props.id}
          name={props.name}
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