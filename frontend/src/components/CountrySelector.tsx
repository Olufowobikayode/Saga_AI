// --- START OF FILE src/components/CountrySelector.tsx ---
'use client';

import React from 'react';
import { countries } from '@/lib/countries'; // Importing our list of countries.

// SAGA UI: Defining the properties for our country selector.
interface CountrySelectorProps {
  id: string;
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
}

/**
 * CountrySelector: A themed dropdown component for selecting a target country.
 * It is styled to match the InputRune for a cohesive form experience.
 */
export default function CountrySelector({ id, label, value, onChange }: CountrySelectorProps) {
  return (
    <div className="w-full">
      <label htmlFor={id} className="block font-serif text-lg text-saga-text-light mb-2">
        {label}
      </label>
      <div className="relative">
        <select
          id={id}
          name={id}
          value={value}
          onChange={onChange}
          // SAGA UI: Applying the same core styles as InputRune for consistency.
          className={`
            w-full appearance-none bg-saga-bg border-2 border-saga-surface rounded-lg
            px-4 py-3 text-saga-text-light
            focus:outline-none focus:ring-2 focus:ring-saga-primary focus:border-transparent
            transition-all duration-300
          `}
        >
          {countries.map((country) => (
            <option key={country.code} value={country.name}>
              {country.name}
            </option>
          ))}
        </select>
        {/* SAGA UI: A custom dropdown arrow to override the browser default. */}
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-saga-text-dark">
          <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
          </svg>
        </div>
      </div>
    </div>
  );
}
// --- END OF FILE src/components/CountrySelector.tsx ---