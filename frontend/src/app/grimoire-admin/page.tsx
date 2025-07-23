// --- START OF FILE src/app/grimoire-admin/page.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import InputRune from '@/components/InputRune';
import SagaButton from '@/components/SagaButton';
import ScriptoriumForm from '@/components/ScriptoriumForm'; // Summoning the real form.

/**
 * The Admin Page: A secure gateway to the Scriptorium where new wisdom is inscribed.
 * This component handles the authentication logic.
 */
export default function GrimoireAdminPage() {
  const [adminKey, setAdminKey] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = () => {
    if (adminKey) {
      // The key is stored to maintain the session.
      // The REAL security check happens on the backend for every API call.
      localStorage.setItem('saga-admin-key', adminKey);
      setIsAuthenticated(true);
      setError('');
    } else {
      setError('An Admin Key must be provided to enter.');
    }
  };
  
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

        {/* SAGA LOGIC: Render the ScriptoriumForm after authentication, not the placeholder. */}
        {isAuthenticated ? (
          <ScriptoriumForm />
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
                type="password"
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