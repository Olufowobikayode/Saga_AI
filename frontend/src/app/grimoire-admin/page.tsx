// --- START OF FILE src/app/grimoire-admin/page.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { GrimoirePage } from '@/services/grimoireApi';
import InputRune from '@/components/InputRune';
import SagaButton from '@/components/SagaButton';
import ScriptoriumForm from '@/components/ScriptoriumForm';
import ManageScrolls from '@/components/ManageScrolls';

// SAGA LOGIC: Defining the possible views within the Scriptorium.
type ScriptoriumView = 'login' | 'manage' | 'edit';

/**
 * The Admin Page: A secure gateway to the Scriptorium, now a full CMS.
 */
export default function GrimoireAdminPage() {
  const [view, setView] = useState<ScriptoriumView>('login');
  const [adminKey, setAdminKey] = useState('');
  const [error, setError] = useState('');
  const [editingScroll, setEditingScroll] = useState<GrimoirePage | null>(null);

  const handleLogin = () => {
    if (adminKey) {
      localStorage.setItem('saga-admin-key', adminKey);
      setView('manage');
      setError('');
    } else {
      setError('An Admin Key must be provided to enter.');
    }
  };
  
  useEffect(() => {
    const storedKey = localStorage.getItem('saga-admin-key');
    if (storedKey) {
      setView('manage');
    }
  }, []);

  // --- SAGA LOGIC: Functions to switch between views ---
  const handleEdit = (scroll: GrimoirePage) => {
    setEditingScroll(scroll);
    setView('edit');
  };

  const handleAddNew = () => {
    setEditingScroll(null);
    setView('edit');
  };
  
  const handleReturnToManager = () => {
    setView('manage');
  };
  
  const renderView = () => {
    switch(view) {
      case 'manage':
        return (
          <motion.div
            key="manage"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <ManageScrolls onEdit={handleEdit} onAddNew={handleAddNew} />
          </motion.div>
        );
      case 'edit':
        return (
          <motion.div
            key="edit"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* We now pass the scroll to edit and the close function to the form */}
            <ScriptoriumForm scroll={editingScroll} onClose={handleReturnToManager} /> 
          </motion.div>
        );
      case 'login':
      default:
        return (
          <motion.div key="login" className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
            <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }} className="space-y-6">
              <InputRune id="adminKey" label="Provide the Sacred Admin Key" placeholder="Enter your secret key..." type="password" value={adminKey} onChange={(e) => setAdminKey(e.target.value)} />
              <SagaButton onClick={handleLogin} className="w-full">Enter the Scriptorium</SagaButton>
              {error && <p className="text-center text-red-400">{error}</p>}
            </form>
          </motion.div>
        );
    }
  }

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Scriptorium
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Where the Keeper inscribes the eternal scrolls.
          </p>
        </header>
        
        <AnimatePresence mode="wait">
          {renderView()}
        </AnimatePresence>

      </div>
    </div>
  );
}
// --- END OF FILE src/app/grimoire-admin/page.tsx ---