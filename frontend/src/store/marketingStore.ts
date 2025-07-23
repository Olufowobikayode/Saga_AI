// --- START OF FILE src/store/marketingStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Adding the final, most detailed states to our workflow.
type ForgeStatus =
  | 'idle' | 'awaiting_anvil' | 'forging_angles' | 'angles_revealed'
  | 'awaiting_platform' | 'awaiting_scribe' | 'forging_asset' | 'asset_revealed'
  | 'unfurling_scroll' // NEW: The ritual for unveiling code or guides.
  | 'scroll_unfurled'  // NEW: Displaying the code or guide.
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
  chosenAngleId: string | null;
  finalAsset: FinalAsset | null;
  
  // This will now hold the content for the "Scroll Unfurled" screen.
  unfurledContent: { title: string; content: string | object; } | null;
  unveiledPrompt: { type: 'Image' | 'Video'; title: string; content: string; } | null;
  
  // Rites (functions)
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, targetAudience: string) => Promise<void>;
  chooseAssetType: (assetType: string) => void;
  choosePlatform: (platform: string) => Promise<void>;
  commandScribe: (length: string) => Promise<void>;
  unfurlScroll: (contentType: 'html_code' | 'deployment_guide') => Promise<void>; // NEW RITE
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
  chosenPlatform: null, chosenAngleId: null, finalAsset: null, 
  unfurledContent: null, unveiledPrompt: null,

  // --- Rites (Functions) ---
  // invokeForge, commandAnvil, chooseAssetType, choosePlatform, and commandScribe remain unchanged.
  // Their logic is already correct for this new flow.
  invokeForge: () => { set({ status: 'awaiting_anvil' }); },
  commandAnvil: async (productName, productDescription, targetAudience) => {
    set({ status: 'forging_angles', error: null });
    try {
      const apiCallPromise = fetch(/*...*/);
      //...
    } catch (err: any) {
      //...
    }
  },
  chooseAssetType: (assetType) => {
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) {
      set({ status: 'awaiting_scribe', chosenAssetType: assetType });
    } else if (['Funnel Page', 'Landing Page', 'Affiliate Review'].includes(assetType)) {
      set({ chosenAssetType: assetType });
      if (assetType === 'Affiliate Review') {
        get().commandScribe('Default');
      } else {
        set({ status: 'awaiting_platform' });
      }
    }
  },
  choosePlatform: async (platform) => {
    set({ chosenPlatform: platform });
    await get().commandScribe('Default');
  },
  commandScribe: async (length) => {
    set({ status: 'forging_asset', error: null });
    try {
      // ... API call logic remains the same
      const [apiResponse] = await Promise.all([/*...*/]);
      set({ status: 'asset_revealed', finalAsset: apiResponse.data });
    } catch (err: any) {
      // ... error handling
    }
  },

  // NEW RITE: Called when a user clicks "View HTML Code" or "View Deployment Guide".
  unfurlScroll: async (contentType) => {
    const { finalAsset } = get();
    if (!finalAsset || !finalAsset[contentType]) return;

    set({ status: 'unfurling_scroll' });
    await performRitual(); // Perform the ad ritual.

    set({
      status: 'scroll_unfurled',
      unfurledContent: finalAsset[contentType],
    });
  },
  
  unveilPrompt: async (type) => {
    // ... logic remains the same
  },

  // This function is now multi-purpose: returns to the main asset selection screen.
  returnToScroll: () => {
    set({ status: 'asset_revealed', unveiledPrompt: null, unfurledContent: null });
  },

  resetForge: () => {
    set({
      status: 'idle', error: null, productName: null, productDescription: null,
      targetAudience: null, angles: [], marketingSessionId: null, chosenAssetType: null,
      chosenPlatform: null, chosenAngleId: null, finalAsset: null, 
      unfurledContent: null, unveiledPrompt: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---