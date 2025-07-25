// --- START OF FILE src/store/contentStore.ts ---
import { create } from 'zustand';
import { useSagaStore } from './sagaStore';

// --- Polling Helper ---
const pollProphecy = (taskId: string, onComplete: (result: any) => void, onError: (error: any) => void) => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;
  const interval = setInterval(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/status/${taskId}`);
      if (!res.ok) throw new Error("Failed to get prophecy status.");
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        clearInterval(interval);
        if (data.result?.error) onError(data.result);
        else onComplete(data.result);
      } else if (data.status === 'FAILURE') {
        clearInterval(interval);
        onError(data.result || { error: "Prophecy failed without a reason." });
      }
    } catch (err) {
      clearInterval(interval);
      onError({ error: "Network error while checking prophecy status.", details: err });
    }
  }, 3000);
};

// --- State Types ---
type LoomStatus = 'idle' | 'awaiting_spark_topic' | 'forging' | 'sparks_revealed' | 'crossroads_revealed' | 'awaiting_final_input' | 'final_content_revealed';
interface ContentSpark { id: string; title: string; description: string; format_suggestion: string; }
interface FinalContent { [key: string]: any; }

interface ContentSagaState {
  status: LoomStatus;
  error: string | null;
  isRitualRunning: boolean;
  
  tacticalInterest: string;
  sparksResult: { sparks: ContentSpark[] } & any | null;
  chosenSpark: ContentSpark | null;
  lastContentType: 'Social Post' | 'Comment' | 'Blog Post' | null;
  lastDetails: any | null;
  finalContent: FinalContent | null;

  // Rites now accept the session ID
  beginWeaving: () => void;
  generateSparks: (topic: string, sessionId: string) => Promise<void>;
  chooseSpark: (sparkId: string) => void;
  forgeContent: (type: 'Social Post' | 'Comment' | 'Blog Post', details: any, sessionId: string) => Promise<void>;
  regenerate: (sessionId: string) => Promise<void>;
  resetLoom: () => void;
  returnToSparks: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useContentStore = create<ContentSagaState>((set, get) => ({
  status: 'idle', error: null, isRitualRunning: false,
  tacticalInterest: '', sparksResult: null, chosenSpark: null, 
  lastContentType: null, lastDetails: null, finalContent: null,
  
  beginWeaving: () => {
    const strategyData = useSagaStore.getState().strategyData;
    const tacticalInterest = strategyData?.prophecy?.the_three_great_sagas[1]?.prime_directive || 'a compelling topic';
    set({ status: 'awaiting_spark_topic', tacticalInterest, error: null });
  },

  generateSparks: async (topic, sessionId) => {
    if (!sessionId) return set({ error: "Session ID missing."});
    const { strategyData } = useSagaStore.getState();
    set({ status: 'forging', isRitualRunning: true, error: null, tacticalInterest: topic });
    
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/content-saga`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          content_type: 'sparks',
          tactical_interest: topic,
          retrieved_histories: strategyData?.retrieved_histories
        })
      });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      const { task_id } = await res.json();

      pollProphecy(task_id,
        (result) => set({ status: 'sparks_revealed', isRitualRunning: false, sparksResult: result }),
        (error) => set({ status: 'awaiting_spark_topic', isRitualRunning: false, error: error.details || error.error })
      );
    } catch (err: any) {
      set({ status: 'awaiting_spark_topic', isRitualRunning: false, error: err.message });
    }
  },

  chooseSpark: (sparkId) => {
    const chosen = get().sparksResult?.sparks.find(s => s.id === sparkId);
    if (chosen) {
      set({ status: 'crossroads_revealed', chosenSpark: chosen });
    }
  },

  forgeContent: async (type, details, sessionId) => {
    if (!sessionId) return set({ error: "Session ID missing."});
    const { chosenSpark } = get();
    if (!chosenSpark) return set({ error: "No content spark was chosen." });

    set({ status: 'forging', isRitualRunning: true, error: null, lastContentType: type, lastDetails: details });
    
    try {
        const res = await fetch(`${API_BASE_URL}/prophesy/content-saga`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                content_type: type.toLowerCase().replace(' ', '_'),
                spark: chosenSpark,
                ...details
            })
        });
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        const { task_id } = await res.json();

        pollProphecy(task_id,
            (result) => set({ status: 'final_content_revealed', isRitualRunning: false, finalContent: {type, ...result} }),
            (error) => set({ status: 'crossroads_revealed', isRitualRunning: false, error: error.details || error.error })
        );
    } catch (err: any) {
        set({ status: 'crossroads_revealed', isRitualRunning: false, error: err.message });
    }
  },
  
  regenerate: async (sessionId) => {
    const { lastContentType, lastDetails } = get();
    if (lastContentType && lastDetails) {
      await get().forgeContent(lastContentType, lastDetails, sessionId);
    }
  },

  resetLoom: () => {
    set({ status: 'idle', error: null, isRitualRunning: false, tacticalInterest: '', sparksResult: null, chosenSpark: null, finalContent: null, lastContentType: null, lastDetails: null });
  },

  returnToSparks: () => {
    set({ status: 'sparks_revealed', chosenSpark: null, finalContent: null });
  }
}));
// --- END OF FILE src/store/contentStore.ts ---