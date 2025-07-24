// --- START OF FILE src/store/ventureStore.ts ---
import { create } from 'zustand';
import { useSagaStore } from './sagaStore';

// SAGA PERSONA: Defining the stages of the Seer's prophecy.
type VentureStatus =
  | 'idle'                    // The Spire is quiet.
  | 'awaiting_refinement'     // Awaiting the user's strategic refinement.
  | 'questing_for_visions'    // The ritual to generate the 10 visions.
  | 'visions_revealed'        // The 10 visions are ready for the user to choose one.
  | 'forging_blueprint'       // The final ritual to generate the business blueprint.
  | 'blueprint_revealed';     // The final blueprint is ready.

// SAGA PERSONA: Defining the structures for the Seer's prophecies.
interface Vision { prophecy_id: string; title: string; one_line_pitch: string; business_model: string; evidence_tag: string; }
interface Blueprint { [key: string]: any; }

// NEW: The structure for the refinement brief.
interface VentureBrief {
  business_model: string;
  primary_strength: string;
  investment_level: string;
}

interface VentureState {
  status: VentureStatus;
  error: string | null;
  ventureSessionId: string | null;
  visions: Vision[];
  chosenVision: Vision | null;
  blueprint: Blueprint | null;

  // The Rites of the Spire
  beginQuest: (brief: VentureBrief) => Promise<void>;
  chooseVision: (visionId: string) => Promise<void>;
  regenerateBlueprint: () => Promise<void>;
  resetSpire: () => void;
  // A simple rite to start the process
  enterSpire: () => void;
}

const API_BASE_URL = 'http://localhost:8000/api/v10';
const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const useVentureStore = create<VentureState>((set, get) => ({
  // --- Initial State ---
  status: 'idle', error: null, ventureSessionId: null,
  visions: [], chosenVision: null, blueprint: null,

  // --- The Rites ---
  enterSpire: () => {
    // This is called when the user first enters the /spire page.
    set({ status: 'awaiting_refinement' });
  },

  beginQuest: async (ventureBrief) => {
    set({ status: 'questing_for_visions', error: null });
    
    const grandStrategyBrief = useSagaStore.getState().brief;
    
    try {
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/new-venture-visions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interest: grandStrategyBrief.interest,
          sub_niche: grandStrategyBrief.subNiche,
          user_content_text: grandStrategyBrief.toneText,
          user_content_url: grandStrategyBrief.toneUrl,
          target_country_name: grandStrategyBrief.targetCountry,
          venture_brief: ventureBrief, // Sending the new, rich brief.
        }),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });

      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);

      set({
        status: 'visions_revealed',
        visions: apiResponse.data.visions,
        ventureSessionId: apiResponse.data.venture_session_id,
      });
    } catch (err: any) {
      set({ status: 'awaiting_refinement', error: err.message || "The mists obscured the Seer's sight." });
    }
  },

  chooseVision: async (visionId) => {
    const chosen = get().visions.find(v => v.prophecy_id === visionId);
    const sessionId = get().ventureSessionId;
    if (!chosen || !sessionId) return;

    set({ status: 'forging_blueprint', chosenVision: chosen, error: null });

    try {
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/new-venture-blueprint`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              venture_session_id: sessionId,
              vision_id: visionId,
          }),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });

      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);

      set({
        status: 'blueprint_revealed',
        blueprint: apiResponse.data.prophecy, // The blueprint is nested under 'prophecy'
      });
    } catch (err: any) {
      set({ status: 'visions_revealed', error: err.message || "The Seer could not forge the blueprint." });
    }
  },

  regenerateBlueprint: async () => {
    const { status, chosenVision } = get();
    if (status === 'blueprint_revealed' && chosenVision) {
      await get().chooseVision(chosenVision.prophecy_id);
    }
  },

  resetSpire: () => {
    set({
      status: 'awaiting_refinement', error: null, visions: [],
      chosenVision: null, blueprint: null,
    });
  },
}));
// --- END OF FILE src/store/ventureStore.ts ---