// --- START OF REFACTORED FILE frontend/src/store/podStore.ts ---
import { create } from 'zustand';
// We no longer need to import useSagaStore here, context will be passed in.

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
  }, 4000);
};

// --- State Types ---
type AnvilStatus = 'idle' | 'awaiting_style' | 'hunting_opportunities' | 'concepts_revealed' | 'forging_package' | 'package_revealed';
interface DesignConcept { concept_id: string; title: string; description: string; justification: string; suggested_products: string[]; }
interface DesignPackage { [key: string]: any; }

interface PODState {
  status: AnvilStatus;
  error: string | null;
  ritualPromise: Promise<any> | null;
  
  nicheInterest: string | null;
  chosenStyle: string | null;
  opportunitiesResult: { design_concepts: DesignConcept[] } & any | null;
  chosenConcept: DesignConcept | null;
  designPackage: DesignPackage | null;

  // Rites of the Anvil
  beginForging: (interest: string) => void; // <-- MODIFIED to accept context
  huntOpportunities: (style: string, sessionId: string) => void;
  chooseConcept: (conceptId: string, sessionId: string) => void;
  regeneratePackage: (sessionId: string) => void;
  resetAnvil: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const usePodStore = create<PODState>((set, get) => ({
  status: 'idle', error: null, ritualPromise: null,
  nicheInterest: null, chosenStyle: null,
  opportunitiesResult: null, chosenConcept: null, designPackage: null,

  // --- MODIFIED RITE ---
  // This rite now explicitly receives the interest from the page component.
  beginForging: (interest: string) => {
    set({ status: 'awaiting_style', nicheInterest: interest, error: null });
  },

  huntOpportunities: (style, sessionId) => {
    // ... (This function remains unchanged)
    if (!sessionId) return set({ error: "Session ID missing." });
    
    const { nicheInterest } = get();
    if (!nicheInterest) return set({ error: "The core niche interest was lost." });
    
    set({ status: 'hunting_opportunities', error: null, chosenStyle: style });
    
    const promise = new Promise(async (resolve, reject) => {
        try {
            const res = await fetch(`${API_BASE_URL}/prophesy/pod/opportunities`, {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ session_id: sessionId, niche_interest: nicheInterest, style: style }),
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
            const { task_id } = await res.json();
      
            pollProphecy(task_id,
              (result) => {
                set({ status: 'concepts_revealed', opportunitiesResult: result });
                resolve(result);
              },
              (error) => {
                const errorMessage = error.details || error.error;
                set({ status: 'awaiting_style', error: errorMessage });
                reject(new Error(errorMessage));
              }
            );
        } catch (err: any) {
            set({ status: 'awaiting_style', error: err.message });
            reject(err);
        }
    });

    set({ ritualPromise: promise });
  },

  chooseConcept: (conceptId, sessionId) => {
    // ... (This function remains unchanged)
    if (!sessionId) return set({ error: "Session ID missing." });
    
    const { opportunitiesResult } = get();
    const chosenConcept = opportunitiesResult?.design_concepts.find(c => c.concept_id === conceptId) || null;
    if (!opportunitiesResult || !chosenConcept) return set({ error: "Session is missing critical context." });
    
    set({ status: 'forging_package', error: null, chosenConcept });
    
    const opportunity_data = { ...opportunitiesResult, ...chosenConcept };

    const promise = new Promise(async (resolve, reject) => {
        try {
            const res = await fetch(`${API_BASE_URL}/prophesy/pod/package`, {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ session_id: sessionId, opportunity_data: opportunity_data }),
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
            const { task_id } = await res.json();
      
            pollProphecy(task_id,
              (result) => {
                set({ status: 'package_revealed', designPackage: result });
                resolve(result);
              },
              (error) => {
                const errorMessage = error.details || error.error;
                set({ status: 'concepts_revealed', error: errorMessage });
                reject(new Error(errorMessage));
              }
            );
        } catch (err: any) {
            set({ status: 'concepts_revealed', error: err.message });
            reject(err)
        }
    });

    set({ ritualPromise: promise });
  },

  regeneratePackage: (sessionId: string) => {
    // ... (This function remains unchanged)
    const { chosenConcept } = get();
    if (chosenConcept) {
      get().chooseConcept(chosenConcept.concept_id, sessionId);
    }
  },

  resetAnvil: () => {
    // ... (This function remains unchanged)
    set({ status: 'concepts_revealed', error: null, chosenConcept: null, designPackage: null });
  },
}));
// --- END OF REFACTORED FILE frontend/src/store/podStore.ts ---