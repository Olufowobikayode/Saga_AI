// --- START OF FILE src/store/podStore.ts ---
import { create } from 'zustand';
import { useSagaStore } from './sagaStore'; // To read the initial briefing.

// SAGA PERSONA: Defining the stages of the Artisan's prophecy.
type AnvilStatus =
  | 'idle'                    // The Anvil is quiet.
  | 'awaiting_style'          // Awaiting the user's choice of artistic style.
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
  ritualPromise: Promise<any> | null; // To hold the promise for the RitualScreen
  
  // Memory of the Artisan
  podSessionId: string | null;
  nicheInterest: string | null; // Will be inherited from the main store.
  chosenStyle: string | null;
  concepts: DesignConcept[];
  chosenConcept: DesignConcept | null;
  designPackage: DesignPackage | null;

  // The Rites of the Anvil
  beginForging: () => void;
  huntOpportunities: (style: string) => Promise<void>;
  chooseConcept: (conceptId: string) => Promise<void>;
  regeneratePackage: () => Promise<void>;
  resetAnvil: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const usePodStore = create<PODState>((set, get) => ({
  // --- Initial State ---
  status: 'idle', error: null, ritualPromise: null, podSessionId: null, nicheInterest: null,
  chosenStyle: null, concepts: [], chosenConcept: null, designPackage: null,

  // --- The Rites ---
  beginForging: () => {
    // Intelligently inherit the niche from the master store.
    const interest = useSagaStore.getState().brief.interest;
    set({ status: 'awaiting_style', nicheInterest: interest, error: null, ritualPromise: null });
  },

  huntOpportunities: async (style) => {
    const nicheInterest = get().nicheInterest;
    if (!nicheInterest) {
      set({ status: 'idle', error: "The core niche interest was lost. Please restart." });
      return;
    }
    
    const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/pod/opportunities`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        niche_interest: nicheInterest,
        style: style
      }),
    }).then(async res => {
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      return res.json();
    });

    set({ status: 'hunting_opportunities', chosenStyle: style, error: null, ritualPromise: apiCallPromise });
    
    try {
      const apiResponse = await apiCallPromise;

      set({
        status: 'concepts_revealed',
        concepts: apiResponse.data.design_concepts,
        podSessionId: apiResponse.data.pod_session_id,
        ritualPromise: null,
      });
    } catch (err: any) {
      set({ status: 'awaiting_style', error: err.message || "The Artisan could not find any opportunities.", ritualPromise: null });
    }
  },

  chooseConcept: async (conceptId) => {
    const chosen = get().concepts.find(c => c.concept_id === conceptId);
    const sessionId = get().podSessionId;
    if (!chosen || !sessionId) return;

    const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/pod/package`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pod_session_id: sessionId, concept_id: conceptId }),
    }).then(async res => {
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      return res.json();
    });

    set({ status: 'forging_package', chosenConcept: chosen, error: null, ritualPromise: apiCallPromise });

    try {
      const apiResponse = await apiCallPromise;
      set({
        status: 'package_revealed',
        designPackage: apiResponse.data,
        ritualPromise: null,
      });
    } catch (err: any) {
      set({ status: 'concepts_revealed', error: err.message || "The Artisan failed to forge the design package.", ritualPromise: null });
    }
  },

  regeneratePackage: async () => {
    const { status, chosenConcept } = get();
    if (status === 'package_revealed' && chosenConcept) {
      await get().chooseConcept(chosenConcept.concept_id);
    }
  },

  resetAnvil: () => {
    // This allows the user to go back from the final package to the list of concepts.
    set({
      status: 'concepts_revealed',
      error: null,
      chosenConcept: null,
      designPackage: null,
      ritualPromise: null,
    });
  },
}));
// --- END OF FILE src/store/podStore.ts ---