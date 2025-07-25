// --- START OF FILE src/store/marketingStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Type definitions for the Skald's Forge workflow.
type ForgeStatus =
  | 'idle' | 'awaiting_anvil' | 'forging_angles' | 'angles_revealed'
  | 'awaiting_platform_html' | 'awaiting_scribe' | 'awaiting_platform_text' 
  | 'forging_asset' | 'asset_revealed' | 'unfurling_scroll' | 'scroll_unfurled' 
  | 'forging_prompt' | 'prompt_unveiled';

interface Angle { angle_id: string; title: string; description: string; framework_steps: string[]; }
interface FinalAsset { [key: string]: any; }

interface MarketingSagaState {
  status: ForgeStatus;
  error: string | null;
  ritualPromise: Promise<any> | null; // To hold the promise for the RitualScreen
  productName: string | null;
  productDescription: string | null;
  targetAudience: string | null;
  angles: Angle[];
  marketingSessionId: string | null;
  chosenAssetType: string | null;
  chosenPlatform: string | null;
  chosenLength: string | null;
  chosenAngleId: string | null; // NEW: To remember the chosen angle for regeneration etc.
  finalAsset: FinalAsset | null;
  unfurledContent: { title: string; content: string | object; } | null;
  unveiledPrompt: { type: 'Image' | 'Video'; title: string; content: string; } | null;
  
  // The Rites of the Forge
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, targetAudience: string) => Promise<void>;
  chooseAngle: (angleId: string) => void;
  chooseAssetType: (assetType: string) => void;
  chooseLength: (length: string) => void;
  choosePlatform: (platform: string) => Promise<void>;
  regenerateAsset: () => Promise<void>;
  unfurlScroll: (contentType: 'html_code' | 'deployment_guide') => Promise<void>;
  unveilPrompt: (type: 'Image' | 'Video') => Promise<void>;
  returnToScroll: () => void;
  resetForge: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

// This internal helper contains the logic for the final API call.
const _forgeFinalAsset = async (get: () => MarketingSagaState, set: (state: Partial<MarketingSagaState>) => void) => {
    const { chosenAngleId, marketingSessionId, chosenAssetType, chosenLength, chosenPlatform } = get();
    if (!chosenAngleId || !marketingSessionId || !chosenAssetType) {
        set({ status: 'idle', error: "A critical error occurred. The strategic session was lost." });
        return;
    }
    
    const requestBody = {
        marketing_session_id: marketingSessionId,
        angle_id: chosenAngleId,
        asset_type: chosenAssetType,
        ...(chosenLength && { length: chosenLength }),
        ...(chosenPlatform && { platform: chosenPlatform }),
    };
    
    const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/marketing/asset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
    }).then(async res => {
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'The Oracle did not respond for the asset prophecy.');
        }
        return res.json();
    });

    set({ status: 'forging_asset', error: null, ritualPromise: apiCallPromise });

    try {
        const apiResponse = await apiCallPromise;
        set({ status: 'asset_revealed', finalAsset: apiResponse.data, ritualPromise: null });
    } catch (err: any) {
        console.error("The asset forging ritual failed:", err);
        set({ status: 'angles_revealed', error: err.message || 'An unknown disturbance occurred.', ritualPromise: null });
    }
};

export const useMarketingStore = create<MarketingSagaState>((set, get) => ({
  status: 'idle', error: null, ritualPromise: null, productName: null, productDescription: null,
  targetAudience: null, angles: [], marketingSessionId: null, chosenAssetType: null,
  chosenPlatform: null, chosenLength: null, chosenAngleId: null, finalAsset: null, 
  unfurledContent: null, unveiledPrompt: null,

  invokeForge: () => { set({ status: 'awaiting_anvil' }); },

  commandAnvil: async (productName, productDescription, targetAudience) => {
    const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/marketing/angles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_name: productName, product_description: productDescription, target_audience: targetAudience, asset_type: 'Ad Copy' }),
    }).then(async res => {
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      return res.json();
    });
    
    set({ status: 'forging_angles', error: null, ritualPromise: apiCallPromise });
    
    try {
      const apiResponse = await apiCallPromise;
      set({ status: 'angles_revealed', productName, productDescription, targetAudience, angles: apiResponse.data.marketing_angles, marketingSessionId: apiResponse.data.marketing_session_id, ritualPromise: null });
    } catch (err: any) {
      set({ status: 'awaiting_anvil', error: err.message || 'An unknown disturbance occurred.', ritualPromise: null });
    }
  },

  chooseAngle: (angleId) => {
    const assetType = get().angles.find(a => a.angle_id === angleId)?.asset_type;
    set({ chosenAngleId: angleId });
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) set({ status: 'awaiting_scribe' });
    else if (['Funnel Page', 'Landing Page'].includes(assetType)) set({ status: 'awaiting_platform_html' });
    else if (['Affiliate Review'].includes(assetType)) _forgeFinalAsset(get, set);
  },

  chooseAssetType: (assetType) => {
    set({ chosenAssetType: assetType, chosenAngleId: get().angles[0].angle_id }); // Auto-select first angle
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) set({ status: 'awaiting_scribe' });
    else if (['Funnel Page', 'Landing Page'].includes(assetType)) set({ status: 'awaiting_platform_html' });
    else if (['Affiliate Review'].includes(assetType)) _forgeFinalAsset(get, set);
  },

  chooseLength: (length) => { set({ status: 'awaiting_platform_text', chosenLength: length }); },
  
  choosePlatform: async (platform) => {
    set({ chosenPlatform: platform });
    await _forgeFinalAsset(get, set);
  },

  regenerateAsset: async () => {
    if (get().status === 'asset_revealed') {
        await _forgeFinalAsset(get, set);
    }
  },

  unfurlScroll: async (contentType) => {
    const { finalAsset } = get();
    if (!finalAsset || !finalAsset[contentType]) return;
    const promise = new Promise(resolve => setTimeout(resolve, 1000));
    set({ status: 'unfurling_scroll', ritualPromise: promise });
    await promise;
    set({ status: 'scroll_unfurled', unfurledContent: finalAsset[contentType], ritualPromise: null });
  },
  
  unveilPrompt: async (type) => {
    const { finalAsset } = get();
    if (!finalAsset) return;
    const promise = new Promise(resolve => setTimeout(resolve, 1000));
    set({ status: 'forging_prompt', ritualPromise: promise });
    await promise;

    let promptData;
    if (type === 'Image') {
        promptData = finalAsset.orb_of_stillness || finalAsset.image_decrees?.[0];
    } else {
        promptData = finalAsset.orb_of_motion;
    }
    if (promptData) {
      set({ status: 'prompt_unveiled', unveiledPrompt: { type, title: promptData.title, content: promptData.description || promptData.prompt }, ritualPromise: null });
    } else {
      set({ status: 'asset_revealed', error: `No ${type} prompt was found.`, ritualPromise: null });
    }
  },

  returnToScroll: () => { set({ status: 'asset_revealed', unveiledPrompt: null, unfurledContent: null, ritualPromise: null }); },

  resetForge: () => {
    set({
      status: 'idle', error: null, ritualPromise: null, productName: null, productDescription: null,
      targetAudience: null, angles: [], marketingSessionId: null, chosenAssetType: null,
      chosenPlatform: null, chosenLength: null, chosenAngleId: null, finalAsset: null, 
      unfurledContent: null, unveiledPrompt: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---