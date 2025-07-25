// --- START OF FILE src/store/ventureStore.ts ---
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
type VentureStatus = 'idle' | 'awaiting_refinement' | 'forging' | 'visions_revealed' | 'blueprint_revealed';
interface Vision { prophecy_id: string; title: string; one_line_pitch: string; business_model: string; evidence_tag: string; }
interface Blueprint { [key: string]: any; }
interface VentureBrief { business_model?: string; primary_strength?: string; investment_level?: string; }

interface VentureState {
  status: VentureStatus;
  error: string | null;
  isRitualRunning: boolean;
  
  // Multi-step context
  visionsResult: { visions: Vision[] } & any | null; // Stores the full result from the first task
  
  chosenVision: Vision | null;
  blueprint: Blueprint | null;

  // Rites
  enterSpire: () => void;
  beginQuest: (ventureBrief: VentureBrief) => Promise<void>;
  chooseVision: (visionId: string) => Promise<void>;
  regenerateBlueprint: () => Promise<void>;
  returnToVisions: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useVentureStore = create<VentureState>((set, get) => ({
  status: 'idle', error: null, isRitualRunning: false,
  visionsResult: null, chosenVision: null, blueprint: null,

  enterSpire: () => set({ status: 'awaiting_refinement' }),

  beginQuest: async (ventureBrief) => {
    const brief = useSagaStore.getState().brief;
    set({ status: 'forging', isRitualRunning: true, error: null });
    
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/new-venture-visions`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interest: brief.interest, sub_niche: brief.subNiche,
          user_content_text: brief.toneText, user_content_url: brief.toneUrl,
          target_country_name: brief.targetCountry, venture_brief: ventureBrief
        }),
      });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      const { task_id } = await res.json();

      pollProphecy(task_id,
        (result) => set({ status: 'visions_revealed', isRitualRunning: false, visionsResult: result }),
        (error) => set({ status: 'awaiting_refinement', isRitualRunning: false, error: error.details || error.error })
      );
    } catch (err: any) {
      set({ status: 'awaiting_refinement', isRitualRunning: false, error: err.message });
    }
  },

  chooseVision: async (visionId) => {
    const { visionsResult } = get();
    const chosenVision = visionsResult?.visions.find(v => v.prophecy_id === visionId) || null;
    if (!visionsResult || !chosenVision) {
      set({ error: "A critical prophecy session error occurred." });
      return;
    }
    set({ chosenVision });
    
    set({ status: 'forging', isRitualRunning: true, error: null });

    try {
      // The second task receives the full context from the first task's result
      const res = await fetch(`${API_BASE_URL}/prophesy/new-venture-blueprint`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              chosen_vision: chosenVision,
              retrieved_histories: visionsResult.retrieved_histories,
              user_tone_instruction: visionsResult.user_tone_instruction,
              country_name: visionsResult.country_name,
          }),
      });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      const { task_id } = await res.json();

      pollProphecy(task_id,
        (result) => set({ status: 'blueprint_revealed', isRitualRunning: false, blueprint: result }),
        (error) => set({ status: 'visions_revealed', isRitualRunning: false, error: error.details || error.error })
      );
    } catch (err: any) {
      set({ status: 'visions_revealed', isRitualRunning: false, error: err.message });
    }
  },

  regenerateBlueprint: async () => {
    const { chosenVision } = get();
    if (chosenVision) {
      await get().chooseVision(chosenVision.prophecy_id);
    }
  },

  returnToVisions: () => {
    set({ status: 'visions_revealed', blueprint: null, chosenVision: null, error: null });
  },
}));
// --- END OF FILE src/store/ventureStore.ts ---