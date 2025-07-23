// --- START OF FILE src/app/grimoire-admin/page.tsx ---
'use client'; // This page uses state for the login form, so it's a client component.

import React, { useState, useEffect } from 'react';
import InputRune from '@/components/InputRune';
import SagaButton from '@/components/SagaButton';

// We will create the ScriptoriumForm component in the next step.
// For now, it is a placeholder that will only be shown *after* successful login.
const ScriptoriumFormPlaceholder = () => (
    <div className="text-center text-saga-primary font-serif text-2xl p-8 bg-saga-surface rounded-lg">
        Authentication successful. The Scriptorium awaits your command.
    </div>
);


/**
 * The Admin Page: A secure gateway to the Scriptorium where new wisdom is inscribed.
 * This component handles the authentication logic.
 */
export default function GrimoireAdminPage() {
  const [adminKey, setAdminKey] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');

  // This function handles the login attempt.
  const handleLogin = () => {
    if (adminKey) {
      // Security Check: In a real-world scenario with multiple users, you would verify this key 
      // with a backend endpoint. For our use case (a single admin), saving the valid key
      // to browser storage is a secure and effective way to maintain the session.
      // The *real* security check happens in the backend on every API call.
      localStorage.setItem('saga-admin-key', adminKey);
      setIsAuthenticated(true);
      setError('');
    } else {
      setError('An Admin Key must be provided to enter.');
    }
  };
  
  // This effect checks if the user is already "logged in" when the page loads.
  useEffect(() => {
    const storedKey = localStorage.getItem('saga-admin-key');
    if (storedKey) {
      setIsAuthenticated(true);
    }
  }, []);

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-3xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Scriptorium
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Where the Keeper inscribes the eternal scrolls.
          </p>
        </header>

        {/* SAGA LOGIC: Conditionally render either the login form or the main content */}
        {isAuthenticated ? (
          <ScriptoriumFormPlaceholder />
        ) : (
          <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
            <form 
                onSubmit={(e) => { e.preventDefault(); handleLogin(); }}
                className="space-y-6"
            >
              <InputRune
                id="adminKey"
                label="Provide the Sacred Admin Key"
                placeholder="Enter your secret key..."
                type="password" // Use password type to hide the key
                value={adminKey}
                onChange={(e) => setAdminKey(e.target.value)}
              />
              <SagaButton onClick={handleLogin} className="w-full">
                Enter the Scriptorium
              </SagaButton>
              {error && <p className="text-center text-red-400">{error}</p>}
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
// --- END OF FILE src/app/grimoire-admin/page.tsx ---