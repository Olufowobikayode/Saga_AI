// --- START OF FILE src/store/ventureStore.ts ---
import { create } from 'zustand';
import { useSagaStore } from './sagaStore'; // To read the initial briefing.

// SAGA PERSONA: Defining the stages of the Seer's prophecy.
type VentureStatus =
  | 'idle'                    // The Spire is quiet.
  | 'performing_entry_rite'   // The ritual upon entering the Spire.
  | 'awaiting_confirmation'   // Awaiting the user's command to begin.
  | 'questing_for_visions'    // The ritual to generate the 10 visions.
  | 'visions_revealed'        // The 10 visions are ready for the user to choose one.
  | 'forging_blueprint'       // The final ritual to generate the business blueprint.
  | 'blueprint_revealed';     // The final blueprint is ready.

// SAGA PERSONA: Defining the structures for the Seer's prophecies.
interface Vision { prophecy_id: string; title: string; one_line_pitch: string; business_model: string; evidence_tag: string; }
interface Blueprint { [key: string]: any; }

interface VentureState {
  status: VentureStatus;
  error: string | null;
  
  // Memory of the Seer
  ventureSessionId: string | null;
  visions: Vision[];
  chosenVision: Vision | null;
  blueprint: Blueprint | null;

  // The Rites of the Spire
  enterSpire: () => Promise<void>;
  beginQuest: () => Promise<void>;
  chooseVision: (visionId: string) => Promise<void>;
  regenerateBlueprint: () => Promise<void>;
  returnToVisions: () => void;
}

const API_BASE_URL = 'http://localhost:8000/api/v10';
const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const useVentureStore = create<VentureState>((set, get) => ({
  // --- Initial State ---
  status: 'idle',
  error: null,
  ventureSessionId: null,
  visions: [],
  chosenVision: null,
  blueprint: null,

  // --- The Rites ---
  enterSpire: async () => {
    set({ status: 'performing_entry_rite', error: null });
    await performRitual();
    set({ status: 'awaiting_confirmation' });
  },

  beginQuest: async () => {
    set({ status: 'questing_for_visions', error: null });
    
    const brief = useSagaStore.getState().brief;
    
    try {
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/new-venture-visions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interest: brief.interest,
          sub_niche: brief.subNiche,
          user_content_text: brief.toneText,
          user_content_url: brief.toneUrl,
          target_country_name: brief.targetCountry,
          // We can use the asset_info from the grand brief as the venture brief
          venture_brief: { 
            business_model: brief.assetType, 
            primary_strength: brief.assetName,
            // We'll need a way to capture investment level, but for now this is a good start.
          }
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
      set({ status: 'awaiting_confirmation', error: err.message || "The mists obscured the Seer's sight." });
    }
  },

  chooseVision: async (visionId) => {
    const chosen = get().visions.find(v => v.prophecy_id === visionId);
    const sessionId = get().ventureSessionId;
    if (!chosen || !sessionId) return;

    set({ status: 'forging_blueprint', chosenVision: chosen, error: null });

    try {
      // THE CORRECTION: This now calls the correct endpoint and sends the correct payload.
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/new-venture-blueprint`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              venture_session_id: sessionId,
              chosen_vision: chosen, // Sending the full object as the backend now expects.
          }),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });

      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);

      set({
        status: 'blueprint_revealed',
        blueprint: apiResponse.data,
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

  returnToVisions: () => {
    set({ status: 'visions_revealed', blueprint: null, error: null });
  },
}));
// --- END OF FILE src/store/ventureStore.ts ---