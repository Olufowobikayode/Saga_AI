// --- START OF FILE src/store/marketingStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Adding a new stage to the ritual for platform selection.
type ForgeStatus =
  | 'idle' | 'awaiting_anvil' | 'forging_angles' | 'angles_revealed'
  | 'awaiting_platform' // NEW: Awaiting the user's choice of HOSTING PLATFORM.
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
  // NEW: Store the chosen platform.
  chosenPlatform: string | null; 
  chosenAngleId: string | null;
  finalAsset: FinalAsset | null;
  unveiledPrompt: { type: 'Image' | 'Video'; title: string; content: string; } | null;
  
  // Rites (functions)
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, targetAudience: string) => Promise<void>;
  chooseAssetType: (assetType: string) => void;
  // NEW: A rite for choosing the platform.
  choosePlatform: (platform: string) => Promise<void>; 
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
  chosenPlatform: null, chosenAngleId: null, finalAsset: null, unveiledPrompt: null,

  // --- Rites (Functions) ---

  invokeForge: () => { set({ status: 'awaiting_anvil' }); },

  commandAnvil: async (productName, productDescription, targetAudience) => {
    set({ status: 'forging_angles', error: null });
    try {
      const apiCallPromise = fetch(/* ... API call remains the same ... */);
      // ... Promise.all logic remains the same
    } catch (err: any) {
      // ... Error handling remains the same
    }
  },

  chooseAssetType: (assetType) => {
    // SAGA LOGIC: The path now forks into three possibilities.
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) {
      set({ status: 'awaiting_scribe', chosenAssetType: assetType });
    } 
    else if (['Funnel Page', 'Landing Page'].includes(assetType)) {
      // NEW: For HTML assets, go to the platform selection screen.
      set({ status: 'awaiting_platform', chosenAssetType: assetType });
    }
    else if (['Affiliate Review'].includes(assetType)) {
      set({ chosenAssetType: assetType });
      get().commandScribe('Default');
    }
  },

  // NEW RITE: Called when a user clicks a platform card.
  choosePlatform: async (platform) => {
    set({ chosenPlatform: platform });
    // After choosing a platform, we immediately forge the asset.
    await get().commandScribe('Default');
  },

  commandScribe: async (length) => {
    // This rite now needs to include the platform in its API call.
    const { angles, marketingSessionId, chosenAssetType, chosenPlatform } = get();
    if (!angles || !marketingSessionId || !chosenAssetType) {
      set({ status: 'idle', error: "A critical error occurred. The strategic session was lost." });
      return;
    }
    
    const chosenAngle = angles[0];
    set({ status: 'forging_asset', error: null, chosenAngleId: chosenAngle.angle_id });

    try {
      // The body of the API call will now include the platform, if it exists.
      const requestBody = {
        marketing_session_id: marketingSessionId,
        angle_id: chosenAngle.angle_id,
        length: length,
        asset_type: chosenAssetType,
        platform: chosenPlatform, // Send the chosen platform to the backend.
      };

      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/marketing/asset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
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
  
  // The rest of the rites remain unchanged...
  unveilPrompt: async (type) => { /* ... same logic ... */ },
  returnToScroll: () => { /* ... same logic ... */ },
  resetForge: () => {
    set({
      status: 'idle', error: null, productName: null, productDescription: null,
      targetAudience: null, angles: [], marketingSessionId: null, chosenAssetType: null,
      chosenPlatform: null, chosenAngleId: null, finalAsset: null, unveiledPrompt: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---