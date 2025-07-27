// --- START OF REFACTORED FILE frontend/src/store/sagaStore.ts ---
import { create } from 'zustand';

// --- Polling Helper ---
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
      } else if (data.status === 'PENDING' || data.status === 'STARTED') {
        // Continue polling, do nothing.
      } else {
        clearInterval(interval);
        onError({ error: `Unexpected prophecy status: ${data.status}` });
      }
    } catch (err) {
      clearInterval(interval);
      onError({ error: "Network error while checking prophecy status.", details: err });
    }
  }, 4000);
};

// --- State Types ---
// MODIFIED: Added a new `prophesied_view` status
type GrandRitualStatus = 'idle' | 'awaiting_query' | 'awaiting_artifact' | 'awaiting_realm' | 'forging' | 'prophesied_hub' | 'prophesied_scroll';
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
  ritualPromise: Promise<any> | null;
  
  beginGrandRitual: () => void;
  submitQuery: (interest: string, subNiche?: string, toneText?: string, toneUrl?: string) => void;
  submitArtifact: (assetType?: string, assetName?: string, assetDescription?: string, promoLinkType?: string, promoLinkUrl?: string) => void;
  submitRealmAndDivine: (targetCountry: string, sessionId: string) => void;
  resetSaga: () => void;

  // --- NEW ACTIONS TO TOGGLE THE VIEW ---
  showStrategyScroll: () => void;
  showTacticalHub: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;
const initialBrief: StrategicBrief = { interest: '' };

export const useSagaStore = create<SagaState>((set, get) => ({
  status: 'idle',
  error: null,
  brief: initialBrief,
  strategyData: null,
  ritualPromise: null,

  beginGrandRitual: () => {
    set({ status: 'awaiting_query', brief: initialBrief, error: null, strategyData: null, ritualPromise: null });
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

  submitRealmAndDivine: (targetCountry: string, sessionId: string) => {
    if (!sessionId) {
      set({ status: 'awaiting_realm', error: "Session ID is missing. The rite cannot proceed." });
      return;
    }
    
    const finalBrief = { ...get().brief, targetCountry };
    set({ status: 'forging', error: null });

    const promise = new Promise(async (resolve, reject) => {
      try {
        const dispatchRes = await fetch(`${API_BASE_URL}/prophesy/grand-strategy`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
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
            // --- MODIFIED: Set initial view to the hub ---
            set({ status: 'prophesied_hub', strategyData: result, brief: finalBrief });
            resolve(result);
          },
          (error) => {
            const errorMessage = error.details || error.error || "An unknown error occurred.";
            set({ status: 'awaiting_realm', error: errorMessage });
            reject(new Error(errorMessage));
          }
        );
      } catch (err: any) {
        set({ status: 'awaiting_realm', error: err.message });
        reject(err);
      }
    });

    set({ ritualPromise: promise });
  },

  resetSaga: () => {
    set({ status: 'idle', error: null, brief: initialBrief, strategyData: null, ritualPromise: null });
  },

  // --- IMPLEMENTATION OF NEW ACTIONS ---
  showStrategyScroll: () => {
    if (get().status === 'prophesied_hub') {
      set({ status: 'prophesied_scroll' });
    }
  },

  showTacticalHub: () => {
    if (get().status === 'prophesied_scroll') {
      set({ status: 'prophesied_hub' });
    }
  },
}));
// --- END OF REFACTORED FILE frontend/src/store/sagaStore.ts ---