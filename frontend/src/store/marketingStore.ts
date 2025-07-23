// --- START OF FILE src/store/marketingStore.ts ---
import { create } from 'zustand';

// --- Type definitions are updated for the new 5-fold structure ---
type ForgeStatus =
  | 'idle' | 'awaiting_anvil' | 'forging_angles' | 'angles_revealed'
  | 'awaiting_scribe' | 'forging_asset' | 'asset_revealed'
  | 'forging_prompt' | 'prompt_unveiled';

interface Angle { angle_id: string; title: string; description: string; framework_steps: string[]; }

// NEW: A more detailed structure for the final prophecy
interface FinalAsset {
  copy?: { title: string; content: string; };
  audience_rune?: { title: string; content: string; };
  platform_sigils?: { title: string; content: string; };
  image_orb?: { title: string; description: string; };
  motion_orb?: { title: string; description: string; };
  // For HTML assets
  html_code?: { title: string; content: string; };
  image_prompts?: { section: string; prompt: string; }[];
  // For Review assets
  reviews?: { content: string }[];
}

interface MarketingSagaState {
  status: ForgeStatus;
  error: string | null;
  productName: string | null;
  productDescription: string | null;
  targetAudience: string | null;
  angles: Angle[];
  marketingSessionId: string | null;
  chosenAssetType: string | null;
  chosenAngleId: string | null;
  finalAsset: FinalAsset | null;
  unveiledPrompt: { type: 'Image' | 'Video'; title: string; content: string; } | null;
  
  // Rites (functions)
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, targetAudience: string) => Promise<void>;
  chooseAssetType: (assetType: string) => void;
  commandScribe: (length: string) => Promise<void>;
  unveilPrompt: (type: 'Image' | 'Video') => Promise<void>;
  returnToScroll: () => void;
  resetForge: () => void;
}

const API_BASE_URL = 'http://localhost:8000/api/v10';
const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const useMarketingStore = create<MarketingSagaState>((set, get) => ({
  // --- Initial State ---
  status: 'idle', error: null, productName: null, productDescription: null,
  targetAudience: null, angles: [], marketingSessionId: null, chosenAssetType: null,
  chosenAngleId: null, finalAsset: null, unveiledPrompt: null,

  // --- Rites (Functions) ---

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
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) {
      set({ status: 'awaiting_scribe', chosenAssetType: assetType });
    } else if (['Funnel Page', 'Landing Page', 'Affiliate Review'].includes(assetType)) {
      set({ chosenAssetType: assetType });
      get().commandScribe('Default');
    }
  },

  commandScribe: async (length) => {
    const { angles, marketingSessionId, chosenAssetType } = get();
    if (!angles || !marketingSessionId || !chosenAssetType) {
      set({ status: 'idle', error: "A critical error occurred. The strategic session was lost." });
      return;
    }
    const chosenAngle = angles[0];
    set({ status: 'forging_asset', error: null, chosenAngleId: chosenAngle.angle_id });
    try {
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/marketing/asset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ marketing_session_id: marketingSessionId, angle_id: chosenAngle.angle_id }),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });
      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);
      set({ status: 'asset_revealed', finalAsset: apiResponse.data });
    } catch (err: any) {
      set({ status: 'angles_revealed', error: err.message || 'An unknown disturbance occurred.' });
    }
  },

  unveilPrompt: async (type) => {
    const { finalAsset } = get();
    if (!finalAsset) return;
    set({ status: 'forging_prompt' });
    await performRitual();
    
    // This logic now needs to handle the different structures
    let promptData;
    if (type === 'Image') {
        promptData = finalAsset.image_prompts ? finalAsset.image_prompts[0] : finalAsset.image_orb;
    } else { // Video
        promptData = finalAsset.motion_orb;
    }

    if (promptData) {
      set({
        status: 'prompt_unveiled',
        unveiledPrompt: {
          type,
          title: promptData.title || promptData.section,
          content: promptData.description || promptData.prompt || "No prompt content found.",
        },
      });
    } else {
      set({ status: 'asset_revealed', error: `No ${type} prompt was found in the prophecy.` });
    }
  },

  returnToScroll: () => {
    set({ status: 'asset_revealed', unveiledPrompt: null });
  },

  resetForge: () => {
    set({
      status: 'idle', error: null, productName: null, productDescription: null,
      targetAudience: null, angles: [], marketingSessionId: null, chosenAssetType: null,
      chosenAngleId: null, finalAsset: null, unveiledPrompt: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---