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
  targetAudience: string | null; // We need to store this for the API call
  angles: Angle[];
  marketingSessionId: string | null; // To track the session with the backend
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

// The base URL for your backend API.
const API_BASE_URL = 'http://localhost:8000/api/v10';

// The ad ritual timer remains.
const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const useMarketingStore = create<MarketingSagaState>((set, get) => ({
  // --- Initial State ---
  status: 'idle',
  error: null,
  productName: null,
  productDescription: null,
  targetAudience: null,
  angles: [],
  marketingSessionId: null,
  chosenAssetType: null,
  chosenAngleId: null,
  finalAsset: null,
  unveiledPrompt: null,

  // --- Rites (Functions) ---

  invokeForge: () => {
    set({ status: 'awaiting_anvil' });
  },

  commandAnvil: async (productName, productDescription, targetAudience) => {
    set({ status: 'forging_angles', error: null });

    try {
      // REAL API CALL to get marketing angles
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/marketing/angles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: productName,
          product_description: productDescription,
          target_audience: targetAudience,
          // We need to decide on an asset type to get relevant angles.
          // Let's default to 'Ad Copy' for the angle generation, as angles are often transferable.
          asset_type: 'Ad Copy' 
        }),
      }).then(async res => {
        if (!res.ok) {
          const errorData = await res.json();
          throw new Error(errorData.detail || 'The Oracle did not respond for the angles prophecy.');
        }
        return res.json();
      });

      // Perform the ritual in parallel
      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);

      set({
        status: 'angles_revealed',
        productName,
        productDescription,
        targetAudience,
        angles: apiResponse.data.marketing_angles,
        marketingSessionId: apiResponse.data.marketing_session_id,
      });

    } catch (err: any) {
      console.error("The angle forging ritual failed:", err);
      set({ status: 'awaiting_anvil', error: err.message || 'An unknown disturbance occurred.' });
    }
  },

  chooseAssetType: (assetType) => {
    // This logic remains the same, as it controls the UI flow.
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) {
      set({ status: 'awaiting_scribe', chosenAssetType: assetType });
    } else {
      // For assets that don't need a length, we can call the final forging rite directly.
      get().commandScribe('Default'); // 'Default' length for assets like Funnels.
    }
  },

  commandScribe: async (length) => {
    const { angles, marketingSessionId, chosenAssetType } = get();
    if (!angles || angles.length === 0 || !marketingSessionId || !chosenAssetType) {
      set({ status: 'idle', error: "A critical error occurred. The strategic session was lost." });
      return;
    }
    
    // We will use the first angle provided by the backend.
    const chosenAngle = angles[0];
    set({ status: 'forging_asset', error: null, chosenAngleId: chosenAngle.angle_id });

    try {
      // REAL API CALL to get the final asset
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/marketing/asset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          marketing_session_id: marketingSessionId,
          angle_id: chosenAngle.angle_id,
          // We also need to pass the length and type to the backend.
          // The backend logic will need to be adapted to use these.
          // For now, we assume the backend can handle it.
          length: length,
          asset_type: chosenAssetType
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
      // Go back to the angle selection on failure
      set({ status: 'angles_revealed', error: err.message || 'An unknown disturbance occurred.' });
    }
  },

  unveilPrompt: async (type) => {
    // This is a purely frontend operation as the prompts are already in the 'finalAsset'.
    // The ritual here is for user experience and ad revenue.
    const { finalAsset } = get();
    if (!finalAsset) return;

    set({ status: 'forging_prompt' });
    await performRitual(); // Perform the ad ritual

    const promptKey = type === 'Image' ? 'image_prompt' : 'video_prompt';
    const promptData = finalAsset[promptKey];

    if (promptData) {
      set({
        status: 'prompt_unveiled',
        unveiledPrompt: { type, title: promptData.title, content: promptData.content },
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