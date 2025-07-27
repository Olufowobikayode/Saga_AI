// --- START OF REFACTORED FILE frontend/src/store/ventureStore.ts ---
import { create } from 'zustand';
import { useSagaStore } from './sagaStore';

// --- Polling Helper ---
// This is the same robust polling function used across stores.
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
type VentureStatus = 'idle' | 'awaiting_refinement' | 'questing_for_visions' | 'visions_revealed' | 'forging_blueprint' | 'blueprint_revealed';
interface Vision { prophecy_id: string; title: string; one_line_pitch: string; business_model: string; evidence_tag: string; }
interface Blueprint { [key: string]: any; }
interface VentureBrief { business_model?: string; primary_strength?: string; investment_level?: string; }

interface VentureState {
  status: VentureStatus;
  error: string | null;
  ritualPromise: Promise<any> | null;
  
  visionsResult: { visions: Vision[] } & any | null;
  chosenVision: Vision | null;
  blueprint: Blueprint | null;

  // Rites now accept the session ID
  enterSpire: () => void;
  beginQuest: (ventureBrief: VentureBrief, sessionId: string) => void;
  chooseVision: (visionId: string, sessionId: string) => void;
  regenerateBlueprint: (sessionId: string) => void;
  returnToVisions: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useVentureStore = create<VentureState>((set, get) => ({
  status: 'idle', error: null, ritualPromise: null,
  visionsResult: null, chosenVision: null, blueprint: null,

  enterSpire: () => set({ status: 'awaiting_refinement' }),

  beginQuest: (ventureBrief, sessionId) => {
    if (!sessionId) return set({ error: "Session ID missing." });
    
    const brief = useSagaStore.getState().brief; // Get context from the main store
    set({ status: 'questing_for_visions', error: null });

    const promise = new Promise(async (resolve, reject) => {
        try {
            const res = await fetch(`${API_BASE_URL}/prophesy/new-venture-visions`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  session_id: sessionId,
                  interest: brief.interest, sub_niche: brief.subNiche,
                  user_content_text: brief.toneText, user_content_url: brief.toneUrl,
                  target_country_name: brief.targetCountry, venture_brief: ventureBrief
                }),
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
            const { task_id } = await res.json();
      
            pollProphecy(task_id,
              (result) => {
                set({ status: 'visions_revealed', visionsResult: result });
                resolve(result);
              },
              (error) => {
                const errorMessage = error.details || error.error;
                set({ status: 'awaiting_refinement', error: errorMessage });
                reject(new Error(errorMessage));
              }
            );
        } catch (err: any) {
            set({ status: 'awaiting_refinement', error: err.message });
            reject(err);
        }
    });

    set({ ritualPromise: promise });
  },

  chooseVision: (visionId, sessionId) => {
    if (!sessionId) return set({ error: "Session ID missing." });

    const { visionsResult } = get();
    const chosenVision = visionsResult?.visions.find(v => v.prophecy_id === visionId) || null;
    if (!visionsResult || !chosenVision) return set({ error: "Session is missing critical context." });
    
    set({ status: 'forging_blueprint', error: null, chosenVision });

    const promise = new Promise(async (resolve, reject) => {
        try {
            const res = await fetch(`${API_BASE_URL}/prophesy/new-venture-blueprint`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    chosen_vision: chosenVision,
                    retrieved_histories: visionsResult.retrieved_histories,
                    user_tone_instruction: visionsResult.user_tone_instruction,
                    country_name: visionsResult.country_name,
                }),
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
            const { task_id } = await res.json();
      
            pollProphecy(task_id,
              (result) => {
                set({ status: 'blueprint_revealed', blueprint: result });
                resolve(result);
              },
              (error) => {
                const errorMessage = error.details || error.error;
                set({ status: 'visions_revealed', error: errorMessage });
                reject(new Error(errorMessage));
              }
            );
        } catch (err: any) {
            set({ status: 'visions_revealed', error: err.message });
            reject(err);
        }
    });
    set({ ritualPromise: promise });
  },

  regenerateBlueprint: (sessionId) => {
    const { chosenVision } = get();
    if (chosenVision) {
      get().chooseVision(chosenVision.prophecy_id, sessionId);
    }
  },

  returnToVisions: () => {
    set({ status: 'visions_revealed', blueprint: null, chosenVision: null, error: null });
  },
}));
// --- END OF REFACTORED FILE frontend/src/store/ventureStore.ts ---