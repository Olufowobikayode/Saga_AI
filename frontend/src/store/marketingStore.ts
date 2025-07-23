// --- START OF FILE src/store/marketingStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Adding a new stage for platform selection for text assets.
type ForgeStatus =
  | 'idle' | 'awaiting_anvil' | 'forging_angles' | 'angles_revealed'
  | 'awaiting_platform_html' // Awaiting platform for HTML assets
  | 'awaiting_scribe'
  | 'awaiting_platform_text' // NEW: Awaiting platform for Text assets
  | 'forging_asset' | 'asset_revealed'
  | 'unfurling_scroll' | 'scroll_unfurled'
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
  chosenLength: string | null; // NEW: Store the chosen length.
  chosenAngleId: string | null;
  finalAsset: FinalAsset | null;
  unfurledContent: { title: string; content: string | object; } | null;
  unveiledPrompt: { type: 'Image' | 'Video'; title: string; content: string; } | null;
  
  // Rites (functions)
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, targetAudience: string) => Promise<void>;
  chooseAssetType: (assetType: string) => void;
  chooseLength: (length: string) => void; // NEW RITE
  choosePlatform: (platform: string) => Promise<void>;
  // commandScribe is now removed, as its logic is merged into choosePlatform
  unfurlScroll: (contentType: 'html_code' | 'deployment_guide') => Promise<void>;
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
  chosenPlatform: null, chosenLength: null, chosenAngleId: null, finalAsset: null, 
  unfurledContent: null, unveiledPrompt: null,

  // --- Rites (Functions) ---

  invokeForge: () => { set({ status: 'awaiting_anvil' }); },

  commandAnvil: async (productName, productDescription, targetAudience) => {
    // ... logic remains the same
  },

  chooseAssetType: (assetType) => {
    set({ chosenAssetType: assetType });
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) {
      set({ status: 'awaiting_scribe' });
    } else if (['Funnel Page', 'Landing Page'].includes(assetType)) {
      set({ status: 'awaiting_platform_html' });
    } else if (['Affiliate Review'].includes(assetType)) {
      // Affiliate reviews don't need length or platform, forge directly.
      get().choosePlatform('Default');
    }
  },

  // NEW RITE: Called from the Scribe's Chamber.
  chooseLength: (length) => {
    set({ status: 'awaiting_platform_text', chosenLength: length });
  },

  // This rite is now multi-purpose, called after choosing a platform for either HTML or Text.
  choosePlatform: async (platform) => {
    const { angles, marketingSessionId, chosenAssetType, chosenLength } = get();
    if (!angles || !marketingSessionId || !chosenAssetType) {
      set({ status: 'idle', error: "A critical error occurred. The strategic session was lost." });
      return;
    }
    
    const chosenAngle = angles[0];
    set({ 
      status: 'forging_asset', 
      error: null, 
      chosenAngleId: chosenAngle.angle_id,
      chosenPlatform: platform,
    });

    try {
      const requestBody = {
        marketing_session_id: marketingSessionId,
        angle_id: chosenAngle.angle_id,
        asset_type: chosenAssetType,
        length: chosenLength, // Will be null for HTML assets, 'Default' for reviews
        platform: platform,   // The chosen platform for any asset type
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
  
  unfurlScroll: async (contentType) => {
    // ... logic remains the same
  },
  
  unveilPrompt: async (type) => {
    // ... logic remains the same
  },

  returnToScroll: () => {
    // This now needs to know where to return to. For simplicity, we'll keep it as is.
    // A more advanced version could remember the previous state.
    set({ status: 'asset_revealed', unveiledPrompt: null, unfurledContent: null });
  },

  resetForge: () => {
    set({
      status: 'idle', error: null, productName: null, productDescription: null,
      targetAudience: null, angles: [], marketingSessionId: null, chosenAssetType: null,
      chosenPlatform: null, chosenLength: null, chosenAngleId: null, finalAsset: null, 
      unfurledContent: null, unveiledPrompt: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---