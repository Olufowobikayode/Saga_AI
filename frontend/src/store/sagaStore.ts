// --- START OF FILE src/store/sagaStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Defining the stages of the new Grand Strategic Ritual.
type GrandRitualStatus =
  | 'idle'                // The ritual has not yet begun.
  | 'awaiting_query'      // The Altar is ready for the user's core query and tone.
  | 'performing_rite_1'   // The first ritual (post-query) is in progress.
  | 'awaiting_artifact'   // Awaiting the user's artifact declaration.
  | 'performing_rite_2'   // The second ritual (post-artifact) is in progress.
  | 'awaiting_realm'      // Awaiting the user's realm selection.
  | 'performing_grand_rite' // The final, grand ritual is in progress.
  | 'prophesied';         // The Grand Strategy is complete, Hall of Prophecies is shown.

// SAGA PERSONA: The full structure of the Strategic Briefing Document.
interface StrategicBrief {
  interest: string;
  subNiche?: string;
  toneText?: string;
  toneUrl?: string;
  assetType?: string;
  assetName?: string;
  assetDescription?: string;
  promoLinkType?: string;
  promoLinkUrl?: string;
  targetCountry?: string;
}

// SAGA PERSONA: Defining the full Master Consciousness.
interface SagaState {
  status: GrandRitualStatus;
  error: string | null;
  brief: StrategicBrief; // The complete briefing document, built step-by-step.
  strategyData: any | null; // Will hold the final Grand Strategy prophecy.

  // The Rites of the multi-stage ritual
  beginGrandRitual: () => void;
  submitQuery: (interest: string, subNiche?: string, toneText?: string, toneUrl?: string) => Promise<void>;
  submitArtifact: (assetType?: string, assetName?: string, assetDescription?: string, promoLinkType?: string, promoLinkUrl?: string) => Promise<void>;
  submitRealmAndDivine: (targetCountry: string) => Promise<void>;
  resetSaga: () => void;
}

const API_BASE_URL = 'http://localhost:8000/api/v10';
const performRitual = (duration: number = 30000) => new Promise(resolve => setTimeout(resolve, duration));

// Initial empty state for the briefing document
const initialBrief: StrategicBrief = { interest: '' };

export const useSagaStore = create<SagaState>((set, get) => ({
  status: 'idle',
  error: null,
  brief: initialBrief,
  strategyData: null,

  // --- THE GRAND RITUAL RITES ---

  beginGrandRitual: () => {
    // Starts the entire journey.
    set({ status: 'awaiting_query', brief: initialBrief, error: null, strategyData: null });
  },

  submitQuery: async (interest, subNiche, toneText, toneUrl) => {
    set({ status: 'performing_rite_1', error: null });
    
    // SAGA LOGIC: In a real app, this might call a lightweight backend endpoint.
    // For now, the ritual is purely for user experience.
    console.log("RITUAL 1: Analyzing core query...");
    await performRitual(); // Perform the 30-second ad ritual.
    
    set(state => ({
      status: 'awaiting_artifact',
      brief: { ...state.brief, interest, subNiche, toneText, toneUrl }
    }));
  },

  submitArtifact: async (assetType, assetName, assetDescription, promoLinkType, promoLinkUrl) => {
    set({ status: 'performing_rite_2', error: null });
    
    // SAGA LOGIC: This ritual could call a backend endpoint to scrape/analyze the provided link.
    console.log("RITUAL 2: Analyzing declared artifact...");
    await performRitual(); // Perform the 30-second ad ritual.

    set(state => ({
      status: 'awaiting_realm',
      brief: { ...state.brief, assetType, assetName, assetDescription, promoLinkType, promoLinkUrl }
    }));
  },

  submitRealmAndDivine: async (targetCountry) => {
    set({ status: 'performing_grand_rite', error: null });

    // SAGA LOGIC: This is the final, major API call.
    // We combine the final piece of data with the rest of the briefing document.
    const finalBrief = { ...get().brief, targetCountry };
    
    try {
      // The backend's GrandStrategy endpoint needs to be able to accept this rich data.
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/grand-strategy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // We need to map our brief to the backend's expected model.
        body: JSON.stringify({
          interest: finalBrief.interest,
          sub_niche: finalBrief.subNiche,
          user_content_text: finalBrief.toneText,
          user_content_url: finalBrief.toneUrl,
          target_country_name: finalBrief.targetCountry,
          // We will need to update the backend to accept these new fields.
          asset_info: {
            type: finalBrief.assetType,
            name: finalBrief.assetName,
            description: finalBrief.assetDescription,
            promo_link: finalBrief.promoLinkUrl,
          }
        }),
      }).then(async res => {
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || 'The Oracle did not respond to the Grand Ritual.');
        }
        return res.json();
      });

      // Perform the final, grand ad ritual.
      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);

      set({
        status: 'prophesied',
        strategyData: apiResponse.data,
        brief: finalBrief, // Save the completed brief
      });

    } catch (err: any) {
      console.error("The Grand Ritual failed:", err);
      // Revert to the final step on failure so the user can retry.
      set({ status: 'awaiting_realm', error: err.message || 'A cosmic disturbance disrupted the Grand Ritual.' });
    }
  },

  resetSaga: () => {
    set({
      status: 'idle',
      error: null,
      brief: initialBrief,
      strategyData: null,
    });
  },
}));
// --- END OF FILE src/store/sagaStore.ts ---