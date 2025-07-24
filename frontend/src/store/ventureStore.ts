// --- START OF FILE src/store/ventureStore.ts ---
import { create } from 'zustand';
import { useSagaStore } from './sagaStore'; // To read the initial briefing.

// SAGA PERSONA: Defining the stages of the Seer's prophecy.
type VentureStatus =
  | 'idle'                    // The Spire is quiet.
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
  ventureSessionId: string | null; // From the backend
  visions: Vision[];
  chosenVision: Vision | null;
  blueprint: Blueprint | null;

  // The Rites of the Spire
  beginQuest: () => Promise<void>;
  chooseVision: (visionId: string) => Promise<void>;
  regenerateBlueprint: () => Promise<void>;
  resetSpire: () => void;
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
  beginQuest: async () => {
    set({ status: 'questing_for_visions', error: null });
    
    // SAGA LOGIC: Intelligently read the context from the master sagaStore.
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
    if (!chosen) return;

    set({ status: 'forging_blueprint', chosenVision: chosen, error: null });

    try {
      // SAGA LOGIC: The backend for this doesn't exist yet, we will need to create it.
      // It should take the venture_session_id and the chosen vision details.
      // For now, we will simulate the API call and response.
      console.log("CALLING BACKEND: prophesy_detailed_blueprint");
      
      const apiCallPromise = new Promise(resolve => resolve({
          data: { 
              prophecy_title: chosen.title,
              summary: "A powerful summary...",
              target_audience: "A detailed description...",
              marketing_plan: {},
              sourcing_and_operations: "Initial counsel...",
              worst_case_monthly_profit_omen: {},
              first_three_steps: ["Step 1...", "Step 2...", "Step 3..."]
          }
      }));

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
      // Re-run the final forging ritual.
      await get().chooseVision(chosenVision.prophecy_id);
    }
  },

  resetSpire: () => {
    set({
      status: 'awaiting_confirmation',
      error: null,
      visions: [],
      chosenVision: null,
      blueprint: null,
      // We keep the ventureSessionId if we want to allow choosing another vision.
    });
  },
}));
// --- END OF FILE src/store/ventureStore.ts ---