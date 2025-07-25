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
  ritualPromise: Promise<any> | null; // To hold the promise for the RitualScreen

  // The Rites of the multi-stage ritual
  beginGrandRitual: () => void;
  submitQuery: (interest: string, subNiche?: string, toneText?: string, toneUrl?: string) => void;
  submitArtifact: (assetType?: string, assetName?: string, assetDescription?: string, promoLinkType?: string, promoLinkUrl?: string) => void;
  submitRealmAndDivine: (targetCountry: string) => void;
  resetSaga: () => void;
}

// CORRECTED: The API URL is now summoned from the scrolls of environment.
const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

// Initial empty state for the briefing document
const initialBrief: StrategicBrief = { interest: '' };

export const useSagaStore = create<SagaState>((set, get) => ({
  status: 'idle',
  error: null,
  brief: initialBrief,
  strategyData: null,
  ritualPromise: null,

  // --- THE GRAND RITUAL RITES ---

  beginGrandRitual: () => {
    // Starts the entire journey.
    set({ status: 'awaiting_query', brief: initialBrief, error: null, strategyData: null, ritualPromise: null });
  },

  submitQuery: async (interest, subNiche, toneText, toneUrl) => {
    const promise = new Promise(resolve => setTimeout(resolve, 5000)); // Simple UX delay
    set({ status: 'performing_rite_1', error: null, ritualPromise: promise });
    
    await promise;
    
    set(state => ({
      status: 'awaiting_artifact',
      brief: { ...state.brief, interest, subNiche, toneText, toneUrl }
    }));
  },

  submitArtifact: async (assetType, assetName, assetDescription, promoLinkType, promoLinkUrl) => {
    const promise = new Promise(resolve => setTimeout(resolve, 5000)); // Simple UX delay
    set({ status: 'performing_rite_2', error: null, ritualPromise: promise });

    await promise;

    set(state => ({
      status: 'awaiting_realm',
      brief: { ...state.brief, assetType, assetName, assetDescription, promoLinkType, promoLinkUrl }
    }));
  },

  submitRealmAndDivine: async (targetCountry) => {
    const finalBrief = { ...get().brief, targetCountry };

    const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/grand-strategy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interest: finalBrief.interest,
          sub_niche: finalBrief.subNiche,
          user_content_text: finalBrief.toneText,
          user_content_url: finalBrief.toneUrl,
          target_country_name: finalBrief.targetCountry,
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

    set({ status: 'performing_grand_rite', error: null, ritualPromise: apiCallPromise });
    
    try {
      const apiResponse = await apiCallPromise;

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
      ritualPromise: null,
    });
  },
}));
// --- END OF FILE src/store/sagaStore.ts ---