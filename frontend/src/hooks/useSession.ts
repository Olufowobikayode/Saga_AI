// --- START OF FILE frontend/src/hooks/useSession.ts ---
'use client';

import { useState, useEffect } from 'react';

const SESSION_STORAGE_KEY = 'saga_session_id';
const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

interface SessionHook {
  sessionId: string | null;
  isLoading: boolean;
}

/**
 * A custom hook to manage the anonymous user session ID.
 * It checks localStorage for an existing ID, and if not found,
 * fetches a new one from the backend and persists it.
 */
export const useSession = (): SessionHook => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initializeSession = async () => {
      try {
        // First, check if the ID already exists in the vessel's memory.
        const storedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);

        if (storedSessionId) {
          setSessionId(storedSessionId);
        } else {
          // If not, we must petition the Oracle for a new identity.
          console.log("No session found. Creating a new one.");
          const response = await fetch(`${API_BASE_URL}/session/create`, {
            method: 'POST',
          });

          if (!response.ok) {
            throw new Error('Failed to create a new session.');
          }

          const data = await response.json();
          const newSessionId = data._id; // The backend returns the ID as '_id'

          if (newSessionId) {
            localStorage.setItem(SESSION_STORAGE_KEY, newSessionId);
            setSessionId(newSessionId);
          } else {
             throw new Error("The Oracle did not provide a valid session ID.");
          }
        }
      } catch (error) {
        console.error("The Rite of Remembrance failed:", error);
        // The app can continue, but some functionality might be limited.
        // We set a null session ID to indicate failure.
        setSessionId(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeSession();
  }, []); // The empty dependency array ensures this rite is performed only once.

  return { sessionId, isLoading };
};
// --- END OF FILE frontend/src/hooks/useSession.ts ---