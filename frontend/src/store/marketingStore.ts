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
  productName: string | null;
  productDescription: string | null;
  targetAudience: string | null;
  angles: Angle[];
  marketingSessionId: string | null;
  chosenAssetType: string | null;
  chosenPlatform: string | null;
  chosenLength: string | null;
  finalAsset: FinalAsset | null;
  unfurledContent: { title: string; content: string | object; } | null;
  unveiledPrompt: { type: 'Image' | 'Video'; title: string; content: string; } | null;
  
  // The Rites of the Forge
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, targetAudience: string) => Promise<void>;
  chooseAssetType: (assetType: string) => void;
  chooseLength: (length: string) => void;
  choosePlatform: (platform: string) => Promise<void>;
  regenerateAsset: () => Promise<void>;
  unfurlScroll: (contentType: 'html_code' | 'deployment_guide') => Promise<void>;
  unveilPrompt: (type: 'Image' | 'Video') => Promise<void>;
  returnToScroll: () => void;
  resetForge: () => void;
}

const API_BASE_URL = 'http://localhost:8000/api/v10';
const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

// This internal helper contains the logic for the final API call.
// It is used by both the initial generation and the regeneration.
const _forgeFinalAsset = async (get: () => MarketingSagaState, set: (state: Partial<MarketingSagaState>) => void) => {
    const { angles, marketingSessionId, chosenAssetType, chosenLength, chosenPlatform } = get();
    if (!angles || !marketingSessionId || !chosenAssetType) {
        set({ status: 'idle', error: "A critical error occurred. The strategic session was lost." });
        return;
    }
    const chosenAngle = angles[0]; // Using the first angle for simplicity.
    set({ status: 'forging_asset', error: null });

    try {
        const requestBody = {
            marketing_session_id: marketingSessionId,
            angle_id: chosenAngle.angle_id,
            asset_type: chosenAssetType,
            length: chosenLength,
            platform: chosenPlatform,
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
        const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);
        set({ status: 'asset_revealed', finalAsset: apiResponse.data });
    } catch (err: any) {
        console.error("The asset forging ritual failed:", err);
        set({ status: 'angles_revealed', error: err.message || 'An unknown disturbance occurred.' });
    }
};

export const useMarketingStore = create<MarketingSagaState>((set, get) => ({
  status: 'idle', error: null, productName: null, productDescription: null,
  targetAudience: null, angles: [], marketingSessionId: null, chosenAssetType: null,
  chosenPlatform: null, chosenLength: null, finalAsset: null, 
  unfurledContent: null, unveiledPrompt: null,

  invokeForge: () => { set({ status: 'awaiting_anvil' }); },

  commandAnvil: async (productName, productDescription, targetAudience) => {
    set({ status: 'forging_angles', error: null });
    try {
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/marketing/angles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: productName, product_description: productDescription, target_audience: targetAudience, asset_type: 'Ad Copy' }),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });
      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);
      set({ status: 'angles_revealed', productName, productDescription, targetAudience, angles: apiResponse.data.marketing_angles, marketingSessionId: apiResponse.data.marketing_session_id });
    } catch (err: any) {
      set({ status: 'awaiting_anvil', error: err.message || 'An unknown disturbance occurred.' });
    }
  },

  chooseAssetType: (assetType) => {
    set({ chosenAssetType: assetType });
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
    set({ status: 'unfurling_scroll' });
    await performRitual();
    set({ status: 'scroll_unfurled', unfurledContent: finalAsset[contentType] });
  },
  
  unveilPrompt: async (type) => {
    const { finalAsset } = get();
    if (!finalAsset) return;
    set({ status: 'forging_prompt' });
    await performRitual();
    let promptData;
    if (type === 'Image') {
        promptData = finalAsset.image_prompts ? finalAsset.image_prompts[0] : finalAsset.image_orb;
    } else {
        promptData = finalAsset.motion_orb;
    }
    if (promptData) {
      set({ status: 'prompt_unveiled', unveiledPrompt: { type, title: promptData.title || promptData.section, content: promptData.description || promptData.prompt || "No prompt content found." }});
    } else {
      set({ status: 'asset_revealed', error: `No ${type} prompt was found.` });
    }
  },

  returnToScroll: () => { set({ status: 'asset_revealed', unveiledPrompt: null, unfurledContent: null }); },

  resetForge: () => {
    set({
      status: 'idle', error: null, productName: null, productDescription: null,
      targetAudience: null, angles: [], marketingSessionId: null, chosenAssetType: null,
      chosenPlatform: null, chosenLength: null, finalAsset: null, 
      unfurledContent: null, unveiledPrompt: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---