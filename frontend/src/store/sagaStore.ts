// --- START OF FILE src/store/sagaStore.ts ---
import { create } from 'zustand';

// --- Polling Helper ---
// This helper remains the same and will be used by all stores.
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
type GrandRitualStatus = 'idle' | 'awaiting_query' | 'awaiting_artifact' | 'awaiting_realm' | 'forging' | 'prophesied';
interface StrategicBrief {
  interest: string; subNiche?: string; toneText?: string; toneUrl?: string;
  assetType?: string; assetName?: string; assetDescription?: string;
  promoLinkType?: string; promoLinkUrl?: string; targetCountry?: string;
}
interface SagaState {
  status: GrandRitualStatus;
  error: string | null;
  brief: StrategicBrief;
  strategyData: any | null;
  isRitualRunning: boolean;
  
  beginGrandRitual: () => void;
  submitQuery: (interest: string, subNiche?: string, toneText?: string, toneUrl?: string) => void;
  submitArtifact: (assetType?: string, assetName?: string, assetDescription?: string, promoLinkType?: string, promoLinkUrl?: string) => void;
  submitRealmAndDivine: (targetCountry: string, sessionId: string) => Promise<void>; // ACCEPTS SESSION ID
  resetSaga: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;
const initialBrief: StrategicBrief = { interest: '' };

export const useSagaStore = create<SagaState>((set, get) => ({
  status: 'idle',
  error: null,
  brief: initialBrief,
  strategyData: null,
  isRitualRunning: false,

  beginGrandRitual: () => {
    set({ status: 'awaiting_query', brief: initialBrief, error: null, strategyData: null, isRitualRunning: false });
  },

  submitQuery: (interest, subNiche, toneText, toneUrl) => {
    set(state => ({
      status: 'awaiting_artifact',
      brief: { ...state.brief, interest, subNiche, toneText, toneUrl }
    }));
  },

  submitArtifact: (assetType, assetName, assetDescription, promoLinkType, promoLinkUrl) => {
    set(state => ({
      status: 'awaiting_realm',
      brief: { ...state.brief, assetType, assetName, assetDescription, promoLinkType, promoLinkUrl }
    }));
  },

  submitRealmAndDivine: async (targetCountry: string, sessionId: string) => {
    if (!sessionId) {
      set({ status: 'awaiting_realm', error: "Session ID is missing. The rite cannot proceed." });
      return;
    }

    set({ status: 'forging', isRitualRunning: true, error: null });
    
    const finalBrief = { ...get().brief, targetCountry };

    try {
      const dispatchRes = await fetch(`${API_BASE_URL}/prophesy/grand-strategy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId, // <-- THE SACRED ID IS NOW INCLUDED
          interest: finalBrief.interest, sub_niche: finalBrief.subNiche,
          user_content_text: finalBrief.toneText, user_content_url: finalBrief.toneUrl,
          target_country_name: finalBrief.targetCountry,
          asset_info: {
            type: finalBrief.assetType, name: finalBrief.assetName,
            description: finalBrief.assetDescription, promo_link: finalBrief.promoLinkUrl,
          }
        }),
      });

      if (!dispatchRes.ok) {
        const err = await dispatchRes.json();
        throw new Error(err.detail || "Failed to dispatch the prophecy.");
      }

      const { task_id } = await dispatchRes.json();

      pollProphecy(
        task_id,
        (result) => {
          set({ status: 'prophesied', strategyData: result, brief: finalBrief, isRitualRunning: false });
        },
        (error) => {
          set({ status: 'awaiting_realm', error: error.details || error.error, isRitualRunning: false });
        }
      );
    } catch (err: any) {
      set({ status: 'awaiting_realm', error: err.message, isRitualRunning: false });
    }
  },

  resetSaga: () => {
    set({ status: 'idle', error: null, brief: initialBrief, strategyData: null, isRitualRunning: false });
  },
}));
// --- END OF FILE src/store/sagaStore.ts ---