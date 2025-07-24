// --- START OF FILE src/store/podStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Defining the stages of the Artisan's prophecy.
type AnvilStatus =
  | 'idle'                    // The Anvil is quiet.
  | 'awaiting_niche'          // Awaiting the user's niche interest.
  | 'hunting_opportunities'   // The ritual to find design concepts.
  | 'concepts_revealed'       // The design concepts are ready for the user to choose one.
  | 'forging_package'         // The final ritual to generate the design & listing package.
  | 'package_revealed';       // The final package is ready.

// SAGA PERSONA: Defining the structures for the Artisan's prophecies.
interface DesignConcept { concept_id: string; title: string; description: string; justification: string; suggested_products: string[]; }
interface DesignPackage { [key: string]: any; }

interface PODState {
  status: AnvilStatus;
  error: string | null;
  
  // Memory of the Artisan
  podSessionId: string | null;
  nicheInterest: string | null;
  concepts: DesignConcept[];
  chosenConcept: DesignConcept | null;
  designPackage: DesignPackage | null;

  // The Rites of the Anvil
  beginForging: () => void;
  huntOpportunities: (nicheInterest: string) => Promise<void>;
  chooseConcept: (conceptId: string) => Promise<void>;
  regeneratePackage: () => Promise<void>;
  resetAnvil: () => void;
}

const API_BASE_URL = 'http://localhost:8000/api/v10';
const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const usePodStore = create<PODState>((set, get) => ({
  // --- Initial State ---
  status: 'idle',
  error: null,
  podSessionId: null,
  nicheInterest: null,
  concepts: [],
  chosenConcept: null,
  designPackage: null,

  // --- The Rites ---
  beginForging: () => {
    set({ status: 'awaiting_niche' });
  },

  huntOpportunities: async (nicheInterest) => {
    set({ status: 'hunting_opportunities', nicheInterest, error: null });
    
    try {
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/pod/opportunities`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ niche_interest: nicheInterest }),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });

      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);

      set({
        status: 'concepts_revealed',
        concepts: apiResponse.data.design_concepts,
        podSessionId: apiResponse.data.pod_session_id,
      });
    } catch (err: any) {
      set({ status: 'awaiting_niche', error: err.message || "The Artisan could not find any opportunities." });
    }
  },

  chooseConcept: async (conceptId) => {
    const chosen = get().concepts.find(c => c.concept_id === conceptId);
    const sessionId = get().podSessionId;
    if (!chosen || !sessionId) return;

    set({ status: 'forging_package', chosenConcept: chosen, error: null });

    try {
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/pod/package`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pod_session_id: sessionId, concept_id: conceptId }),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });

      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);

      set({
        status: 'package_revealed',
        designPackage: apiResponse.data,
      });
    } catch (err: any) {
      set({ status: 'concepts_revealed', error: err.message || "The Artisan failed to forge the design package." });
    }
  },

  regeneratePackage: async () => {
    const { status, chosenConcept } = get();
    if (status === 'package_revealed' && chosenConcept) {
      await get().chooseConcept(chosenConcept.concept_id);
    }
  },

  resetAnvil: () => {
    set({
      status: 'awaiting_niche',
      error: null,
      concepts: [],
      chosenConcept: null,
      designPackage: null,
      // We keep the podSessionId to allow choosing another concept from the same hunt.
    });
  },
}));
// --- END OF FILE src/store/podStore.ts ---