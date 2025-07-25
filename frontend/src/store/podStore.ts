// --- START OF FILE src/store/podStore.ts ---
import { create } from 'zustand';
import { useSagaStore } from './sagaStore';

// Shared Polling Helper
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
type AnvilStatus = 'idle' | 'awaiting_style' | 'forging' | 'concepts_revealed' | 'package_revealed';
interface DesignConcept { concept_id: string; title: string; description: string; justification: string; suggested_products: string[]; }
interface DesignPackage { [key: string]: any; }

interface PODState {
  status: AnvilStatus;
  error: string | null;
  isRitualRunning: boolean;
  
  // Memory & Context
  nicheInterest: string | null;
  chosenStyle: string | null;

  // Multi-step context
  opportunitiesResult: { design_concepts: DesignConcept[] } & any | null;
  
  chosenConcept: DesignConcept | null;
  designPackage: DesignPackage | null;

  // Rites
  beginForging: () => void;
  huntOpportunities: (style: string) => Promise<void>;
  chooseConcept: (conceptId: string) => Promise<void>;
  regeneratePackage: () => Promise<void>;
  resetAnvil: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const usePodStore = create<PODState>((set, get) => ({
  status: 'idle', error: null, isRitualRunning: false,
  nicheInterest: null, chosenStyle: null,
  opportunitiesResult: null, chosenConcept: null, designPackage: null,

  beginForging: () => {
    const interest = useSagaStore.getState().brief.interest;
    set({ status: 'awaiting_style', nicheInterest: interest, error: null });
  },

  huntOpportunities: async (style) => {
    const { nicheInterest } = get();
    if (!nicheInterest) {
      set({ status: 'idle', error: "The core niche interest was lost. Please restart." });
      return;
    }
    set({ status: 'forging', isRitualRunning: true, error: null, chosenStyle: style });
    
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/pod/opportunities`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ niche_interest: nicheInterest, style: style }),
      });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      const { task_id } = await res.json();

      pollProphecy(task_id,
        (result) => set({ status: 'concepts_revealed', isRitualRunning: false, opportunitiesResult: result }),
        (error) => set({ status: 'awaiting_style', isRitualRunning: false, error: error.details || error.error })
      );
    } catch (err: any) {
      set({ status: 'awaiting_style', isRitualRunning: false, error: err.message });
    }
  },

  chooseConcept: async (conceptId) => {
    const { opportunitiesResult } = get();
    const chosenConcept = opportunitiesResult?.design_concepts.find(c => c.concept_id === conceptId) || null;
    if (!opportunitiesResult || !chosenConcept) {
      set({ error: "A critical prophecy session error occurred." });
      return;
    }
    
    set({ status: 'forging', isRitualRunning: true, error: null, chosenConcept });
    
    const opportunityData = { ...opportunitiesResult, ...chosenConcept };

    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/pod/package`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opportunity_data: opportunityData }),
      });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      const { task_id } = await res.json();

      pollProphecy(task_id,
        (result) => set({ status: 'package_revealed', isRitualRunning: false, designPackage: result }),
        (error) => set({ status: 'concepts_revealed', isRitualRunning: false, error: error.details || error.error })
      );
    } catch (err: any) {
      set({ status: 'concepts_revealed', isRitualRunning: false, error: err.message });
    }
  },

  regeneratePackage: async () => {
    const { chosenConcept } = get();
    if (chosenConcept) {
      await get().chooseConcept(chosenConcept.concept_id);
    }
  },

  resetAnvil: () => {
    set({
      status: 'concepts_revealed',
      error: null,
      chosenConcept: null,
      designPackage: null,
    });
  },
}));
// --- END OF FILE src/store/podStore.ts ---