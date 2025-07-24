// --- START OF FILE src/components/ManageScrolls.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import { GrimoirePage, getAllScrolls, deleteScroll } from '@/services/grimoireApi';
import { motion, AnimatePresence } from 'framer-motion';

// SAGA LOGIC: Define the properties for this component.
// It needs functions to tell the parent component which action to take.
interface ManageScrollsProps {
  onEdit: (scroll: GrimoirePage) => void;
  onAddNew: () => void;
}

/**
 * ManageScrolls: The main dashboard for the Scriptorium. Displays a list of all
 * existing posts with options to edit, delete, or create a new one.
 */
export default function ManageScrolls({ onEdit, onAddNew }: ManageScrollsProps) {
  const [scrolls, setScrolls] = useState<GrimoirePage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // SAGA LOGIC: Fetch all scrolls from the Grimoire when the component loads.
  const fetchScrolls = async () => {
    setIsLoading(true);
    const fetchedScrolls = await getAllScrolls();
    setScrolls(fetchedScrolls);
    setIsLoading(false);
  };

  useEffect(() => {
    fetchScrolls();
  }, []);

  // SAGA LOGIC: Handle the deletion of a scroll.
  const handleDelete = async (id: string, title: string) => {
    // A confirmation step to prevent accidental banishment.
    if (!window.confirm(`Are you sure you wish to banish the scroll "${title}" forever? This action cannot be undone.`)) {
      return;
    }
    
    const adminKey = localStorage.getItem('saga-admin-key');
    if (!adminKey) {
      setError("Authentication error. The sacred key is missing.");
      return;
    }

    const result = await deleteScroll(id, adminKey);
    if (result.success) {
      setMessage(result.message);
      // Refresh the list after successful deletion.
      fetchScrolls();
    } else {
      setError(result.message);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-saga-surface p-8 rounded-lg border border-white/10"
    >
      <div className="flex justify-between items-center border-b border-white/20 pb-4 mb-6">
        <h2 className="font-serif text-3xl text-saga-primary">Manage Scrolls</h2>
        <button
          onClick={onAddNew}
          className="bg-saga-primary text-white font-bold py-2 px-4 rounded-lg hover:brightness-110 transition-all"
        >
          + Divine New Scroll
        </button>
      </div>

      {message && <p className="text-center text-green-400 mb-4">{message}</p>}
      {error && <p className="text-center text-red-400 mb-4">{error}</p>}

      {isLoading ? (
        <p className="text-center text-saga-text-dark">Summoning the list of scrolls...</p>
      ) : (
        <div className="space-y-4">
          <AnimatePresence>
            {scrolls.length > 0 ? (
              scrolls.map((scroll) => (
                <motion.div
                  key={scroll.id}
                  layout
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -300, transition: { duration: 0.3 } }}
                  className="flex justify-between items-center bg-saga-bg p-4 rounded-md"
                >
                  <div>
                    <h3 className="font-semibold text-lg text-saga-text-light">{scroll.title}</h3>
                    <p className="text-sm text-saga-text-dark">/{scroll.slug}</p>
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => onEdit(scroll)}
                      className="text-saga-secondary hover:brightness-125"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(scroll.id, scroll.title)}
                      className="text-red-500 hover:text-red-400"
                    >
                      Delete
                    </button>
                  </div>
                </motion.div>
              ))
            ) : (
              <p className="text-center text-saga-text-dark py-4">The Grimoire is empty.</p>
            )}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
}
// --- END OF FILE src/components/ManageScrolls.tsx ---