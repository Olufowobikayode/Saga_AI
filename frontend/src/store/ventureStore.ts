// --- START OF FILE src/store/ventureStore.ts ---
import { create } from 'zustand';
import { useSagaStore } from './sagaStore'; // To read the initial briefing.

// SAGA PERSONA: Defining the stages of the Seer's prophecy.
type VentureStatus =
  | 'idle'                    // The Spire is quiet.
  | 'performing_entry_rite'   // The ritual upon entering the Spire.
  | 'awaiting_refinement'     // Awaiting user's refinement of the venture quest.
  | 'questing_for_visions'    // The ritual to generate the 10 visions.
  | 'visions_revealed'        // The 10 visions are ready for the user to choose one.
  | 'forging_blueprint'       // The final ritual to generate the business blueprint.
  | 'blueprint_revealed';     // The final blueprint is ready.

// SAGA PERSONA: Defining the structures for the Seer's prophecies.
interface Vision { prophecy_id: string; title: string; one_line_pitch: string; business_model: string; evidence_tag: string; }
interface Blueprint { [key: string]: any; }
interface VentureBrief { business_model?: string; primary_strength?: string; investment_level?: string; }

interface VentureState {
  status: VentureStatus;
  error: string | null;
  ritualPromise: Promise<any> | null;
  
  // Memory of the Seer
  ventureSessionId: string | null;
  visions: Vision[];
  chosenVision: Vision | null;
  blueprint: Blueprint | null;

  // The Rites of the Spire
  enterSpire: () => Promise<void>;
  beginQuest: (ventureBrief: VentureBrief) => Promise<void>;
  chooseVision: (visionId: string) => Promise<void>;
  regenerateBlueprint: () => Promise<void>;
  returnToVisions: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useVentureStore = create<VentureState>((set, get) => ({
  // --- Initial State ---
  status: 'idle',
  error: null,
  ritualPromise: null,
  ventureSessionId: null,
  visions: [],
  chosenVision: null,
  blueprint: null,

  // --- The Rites ---
  enterSpire: async () => {
    const promise = new Promise(resolve => setTimeout(resolve, 1000));
    set({ status: 'performing_entry_rite', error: null, ritualPromise: promise });
    await promise;
    set({ status: 'awaiting_refinement', ritualPromise: null });
  },

  beginQuest: async (ventureBrief) => {
    const brief = useSagaStore.getState().brief;
    
    const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/new-venture-visions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interest: brief.interest,
          sub_niche: brief.subNiche,
          user_content_text: brief.toneText,
          user_content_url: brief.toneUrl,
          target_country_name: brief.targetCountry,
          venture_brief: ventureBrief
        }),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });

    set({ status: 'questing_for_visions', error: null, ritualPromise: apiCallPromise });
    
    try {
      const apiResponse = await apiCallPromise;
      set({
        status: 'visions_revealed',
        visions: apiResponse.data.visions,
        ventureSessionId: apiResponse.data.venture_session_id,
        ritualPromise: null,
      });
    } catch (err: any) {
      set({ status: 'awaiting_refinement', error: err.message || "The mists obscured the Seer's sight.", ritualPromise: null });
    }
  },

  chooseVision: async (visionId) => {
    const chosen = get().visions.find(v => v.prophecy_id === visionId);
    const sessionId = get().ventureSessionId;
    if (!chosen || !sessionId) return;

    const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/new-venture-blueprint`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              venture_session_id: sessionId,
              chosen_vision: chosen,
          }),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });

    set({ status: 'forging_blueprint', chosenVision: chosen, error: null, ritualPromise: apiCallPromise });

    try {
      const apiResponse = await apiCallPromise;
      set({
        status: 'blueprint_revealed',
        blueprint: apiResponse.data,
        ritualPromise: null,
      });
    } catch (err: any) {
      set({ status: 'visions_revealed', error: err.message || "The Seer could not forge the blueprint.", ritualPromise: null });
    }
  },

  regenerateBlueprint: async () => {
    const { status, chosenVision } = get();
    if (status === 'blueprint_revealed' && chosenVision) {
      await get().chooseVision(chosenVision.prophecy_id);
    }
  },

  returnToVisions: () => {
    set({ status: 'visions_revealed', blueprint: null, error: null, ritualPromise: null });
  },
}));
// --- END OF FILE src/store/ventureStore.ts ---