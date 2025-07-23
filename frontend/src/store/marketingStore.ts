// --- START OF FILE src/store/marketingStore.ts ---
import { create } from 'zustand';

// --- Type definitions remain the same ---
type ForgeStatus =
  | 'idle' | 'awaiting_anvil' | 'forging_angles' | 'angles_revealed'
  | 'awaiting_scribe' | 'forging_asset' | 'asset_revealed'
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
  chosenAngleId: string | null;
  finalAsset: FinalAsset | null;
  unveiledPrompt: { type: 'Image' | 'Video'; title: string; content: string; } | null;
  
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

  invokeForge: () => {
    set({ status: 'awaiting_anvil' });
  },

  commandAnvil: async (productName, productDescription, targetAudience) => {
    set({ status: 'forging_angles', error: null });
    try {
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/marketing/angles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: productName,
          product_description: productDescription,
          target_audience: targetAudience,
          asset_type: 'Ad Copy' // Angles are generally transferable
        }),
      }).then(async res => {
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || 'The Oracle did not respond for the angles prophecy.');
        }
        return res.json();
      });
      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);
      set({
        status: 'angles_revealed', productName, productDescription, targetAudience,
        angles: apiResponse.data.marketing_angles,
        marketingSessionId: apiResponse.data.marketing_session_id,
      });
    } catch (err: any) {
      console.error("The angle forging ritual failed:", err);
      set({ status: 'awaiting_anvil', error: err.message || 'An unknown disturbance occurred.' });
    }
  },

  chooseAssetType: (assetType) => {
    // SAGA LOGIC: This is the key change.
    // If the asset type is text-based, go to the Scribe's Chamber.
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) {
      set({ status: 'awaiting_scribe', chosenAssetType: assetType });
    } 
    // If the asset type is HTML-based or a review, we can forge it directly.
    else if (['Funnel Page', 'Landing Page', 'Affiliate Review'].includes(assetType)) {
      // We set the chosen asset type and then call the final forging rite directly.
      set({ chosenAssetType: assetType });
      get().commandScribe('Default'); // 'Default' length is a signal for non-text assets.
    }
  },

  commandScribe: async (length) => {
    const { angles, marketingSessionId, chosenAssetType } = get();
    if (!angles || angles.length === 0 || !marketingSessionId || !chosenAssetType) {
      set({ status: 'idle', error: "A critical error occurred. The strategic session was lost." });
      return;
    }
    
    const chosenAngle = angles[0];
    set({ status: 'forging_asset', error: null, chosenAngleId: chosenAngle.angle_id });

    try {
      // The backend API call is the same, but the backend will return a different
      // JSON structure for HTML assets vs. text assets.
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/marketing/asset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          marketing_session_id: marketingSessionId,
          angle_id: chosenAngle.angle_id,
          // The backend's `MarketingSagaStack` needs to know the asset_type to call the correct method.
          // Our `server.py` already handles this logic.
        }),
      }).then(async res => {
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || 'The Oracle did not respond for the asset prophecy.');
        }
        return res.json();
      });

      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);

      set({
        status: 'asset_revealed',
        finalAsset: apiResponse.data,
      });

    } catch (err: any) {
      console.error("The asset forging ritual failed:", err);
      set({ status: 'angles_revealed', error: err.message || 'An unknown disturbance occurred.' });
    }
  },

  unveilPrompt: async (type) => {
    const { finalAsset } = get();
    if (!finalAsset) return;
    set({ status: 'forging_prompt' });
    await performRitual();
    const promptKey = type === 'Image' ? 'image_prompt' : 'video_prompt';
    // For HTML assets, the image prompts might be in an array.
    const promptData = Array.isArray(finalAsset.image_prompts) 
      ? finalAsset.image_prompts[0] // Just grab the first one for now
      : finalAsset[promptKey];

    if (promptData) {
      set({
        status: 'prompt_unveiled',
        unveiledPrompt: { type, title: promptData.title || promptData.section, content: promptData.content || promptData.prompt },
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