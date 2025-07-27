// --- START OF REFACTORED FILE frontend/src/store/marketingStore.ts ---
import { create } from 'zustand';

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
  }, 4000);
};

// --- State Types ---
type ForgeStatus = 'idle' | 'awaiting_anvil' | 'forging_angles' | 'angles_revealed' | 'awaiting_platform_html' | 'awaiting_scribe' | 'awaiting_platform_text' | 'forging_asset' | 'asset_revealed' | 'prompt_unveiled' | 'scroll_unfurled';
interface Angle { angle_id: string; title: string; description: string; framework_of_conquest: string[]; }
interface FinalAsset { [key: string]: any; }

interface MarketingSagaState {
  status: ForgeStatus;
  error: string | null;
  ritualPromise: Promise<any> | null;
  
  // No need to store saga context here, it's used immediately.
  anglesResult: { marketing_angles: Angle[] } & any | null;
  chosenAssetType: string | null;
  finalAsset: FinalAsset | null;
  unveiledPrompt: { type: 'Image' | 'Video', title: string, content: string } | null;
  unfurledScroll: { title: string, content: string | object } | null;

  // Rites of the Forge
  invokeForge: () => void; // MODIFIED: No longer needs context, page will handle it.
  commandAnvil: (productName: string, productDescription: string, targetAudience: string, sessionId: string) => void;
  chooseAssetType: (assetType: string) => void;
  choosePlatform: (platform: string, sessionId: string) => void;
  chooseLength: (length: string, sessionId: string) => void;
  regenerateAsset: (sessionId: string) => void;
  unveilPrompt: (type: 'Image' | 'Video') => void;
  unfurlScroll: (scrollType: 'html_code' | 'deployment_guide') => void;
  returnToScroll: () => void;
  resetForge: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useMarketingStore = create<MarketingSagaState>((set, get) => ({
  status: 'idle', error: null, ritualPromise: null,
  anglesResult: null, chosenAssetType: null,
  finalAsset: null, unveiledPrompt: null, unfurledScroll: null,
  
  // --- MODIFIED RITE ---
  // The page component now handles checking for context. This rite just sets the status.
  invokeForge: () => set({ status: 'awaiting_anvil' }),

  commandAnvil: (productName, productDescription, targetAudience, sessionId) => {
    // ... (This function remains unchanged)
    if (!sessionId) return set({ error: "Session ID missing." });

    set({ status: 'forging_angles', error: null });

    const promise = new Promise(async (resolve, reject) => {
        try {
            const res = await fetch(`${API_BASE_URL}/prophesy/marketing/angles`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, product_name: productName, product_description: productDescription, target_audience: targetAudience, asset_type: 'Marketing Angles' })
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
            const { task_id } = await res.json();
          
            pollProphecy(task_id,
                (result) => {
                    set({ status: 'angles_revealed', anglesResult: result });
                    resolve(result);
                },
                (error) => {
                    const msg = error.details || error.error;
                    set({ status: 'awaiting_anvil', error: msg });
                    reject(new Error(msg));
                }
            );
        } catch (err: any) {
            set({ status: 'awaiting_anvil', error: err.message });
            reject(err);
        }
    });

    set({ ritualPromise: promise });
  },

  chooseAssetType: (assetType) => {
    // ... (This function remains unchanged)
     const isHtml = ['Funnel Page', 'Landing Page'].includes(assetType);
    const isText = ['Ad Copy', 'Email Copy', 'Affiliate Copy'].includes(assetType);
    
    let nextStatus: ForgeStatus = 'awaiting_scribe'; // Default
    if (isHtml) nextStatus = 'awaiting_platform_html';
    else if (isText) nextStatus = 'awaiting_platform_text';
    
    set({ chosenAssetType: assetType, status: nextStatus });
  },

  // Need to define the internal helper `_forgeFinalAsset` that was referenced but not included before.
  _forgeFinalAsset: (details: { platform?: string; length?: string; }, sessionId: string) => {
    if (!sessionId) return set({ error: "Session ID missing." });
    
    const { anglesResult, chosenAssetType } = get();
    if (!anglesResult || !chosenAssetType) return set({ error: "Session is missing critical context." });
    
    const angle_data = { ...anglesResult, asset_type: chosenAssetType };
    
    set({ status: 'forging_asset', error: null });
    const promise = new Promise(async (resolve, reject) => {
        try {
            const res = await fetch(`${API_BASE_URL}/prophesy/marketing/asset`, {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ session_id: sessionId, angle_data: angle_data, ...details })
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
            const { task_id } = await res.json();
      
            pollProphecy(task_id,
              (result) => {
                set({ status: 'asset_revealed', finalAsset: result });
                resolve(result);
              },
              (error) => {
                const msg = error.details || error.error;
                set({ status: 'angles_revealed', error: msg });
                reject(new Error(msg));
              }
            );
        } catch (err: any) {
            set({ status: 'angles_revealed', error: err.message });
            reject(err);
        }
    });
    set({ ritualPromise: promise });
  },
  
  choosePlatform: (platform: string, sessionId: string) => {
    // @ts-ignore - The function exists but might not be visible to the public type
    get()._forgeFinalAsset({ platform }, sessionId);
  },

  chooseLength: (length: string, sessionId: string) => {
    // @ts-ignore
    get()._forgeFinalAsset({ length }, sessionId);
  },

  regenerateAsset: (sessionId: string) => {
    console.warn("Regeneration should be re-triggered from the component providing the context.");
  },

  unveilPrompt: (type) => {
    // ... (This function remains unchanged)
    const { finalAsset } = get();
    if (!finalAsset) return;
    const orb = type === 'Image' ? finalAsset.image_orb : finalAsset.motion_orb;
    if (orb) {
      set({ status: 'prompt_unveiled', unveiledPrompt: { type, title: orb.title, content: orb.description } });
    }
  },

  unfurlScroll: (scrollType) => {
    // ... (This function remains unchanged)
    const { finalAsset } = get();
    if (!finalAsset || !finalAsset[scrollType]) return;
    set({ status: 'scroll_unfurled', unfurledScroll: finalAsset[scrollType] });
  },
  
  returnToScroll: () => set({ status: 'asset_revealed', unveiledPrompt: null, unfurledScroll: null }),
  
  resetForge: () => {
    // ... (This function remains unchanged)
    set({ status: 'awaiting_anvil', error: null, ritualPromise: null, anglesResult: null, chosenAssetType: null, finalAsset: null, unveiledPrompt: null, unfurledScroll: null });
  },
}));
// --- END OF REFACTORED FILE frontend/src/store/marketingStore.ts ---