// --- START OF FILE src/store/marketingStore.ts ---
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
  }, 3000);
};

// --- State Types ---
type ForgeStatus = 'idle' | 'awaiting_anvil' | 'forging' | 'angles_revealed' | 'awaiting_final_input' | 'asset_revealed' | 'viewing_detail';
interface Angle { angle_id: string; title: string; description: string; framework_of_conquest: string[]; }
interface FinalAsset { [key: string]: any; }

interface MarketingSagaState {
  status: ForgeStatus;
  error: string | null;
  isRitualRunning: boolean;
  
  productName: string | null;
  productDescription: string | null;
  targetAudience: string | null;
  anglesResult: { marketing_angles: Angle[] } & any | null;
  chosenAngle: Angle | null;
  chosenAssetType: string | null;
  finalAsset: FinalAsset | null;
  detailedContent: { title: string; content: string | object; type: 'scroll' | 'prompt_image' | 'prompt_video' } | null;

  // Rites now accept the session ID
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, targetAudience: string, sessionId: string) => Promise<void>;
  chooseAngleAndAsset: (angleId: string, assetType: string) => Promise<void>;
  forgeFinalAsset: (details: { platform?: string; length?: string; }, sessionId: string) => Promise<void>;
  regenerateAsset: () => void; // Becomes simpler
  viewDetail: (contentType: 'html_code' | 'deployment_guide' | 'image' | 'video') => void;
  returnToAsset: () => void;
  resetForge: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useMarketingStore = create<MarketingSagaState>((set, get) => ({
  status: 'idle', error: null, isRitualRunning: false,
  productName: null, productDescription: null, targetAudience: null,
  anglesResult: null, chosenAngle: null, chosenAssetType: null,
  finalAsset: null, detailedContent: null,
  
  invokeForge: () => set({ status: 'awaiting_anvil' }),

  commandAnvil: async (productName, productDescription, targetAudience, sessionId) => {
    if (!sessionId) return set({ error: "Session ID missing." });
    set({ status: 'forging', isRitualRunning: true, error: null });
    
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/marketing/angles`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, product_name: productName, product_description: productDescription, target_audience: targetAudience, asset_type: 'Ad Copy' })
      });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      const { task_id } = await res.json();
      
      pollProphecy(task_id,
        (result) => set({ status: 'angles_revealed', isRitualRunning: false, anglesResult: result, productName, productDescription, targetAudience }),
        (error) => set({ status: 'awaiting_anvil', isRitualRunning: false, error: error.details || error.error })
      );
    } catch (err: any) {
      set({ status: 'awaiting_anvil', isRitualRunning: false, error: err.message });
    }
  },

  chooseAngleAndAsset: async (angleId, assetType) => {
    const chosenAngle = get().anglesResult?.marketing_angles.find(a => a.angle_id === angleId) || null;
    set({ chosenAngle, chosenAssetType: assetType });

    if (['Affiliate Review'].includes(assetType)) {
      // Forge immediately, but we need the session ID from the component.
      // This highlights a flow change: the component will now call forgeFinalAsset directly.
      set({ status: 'awaiting_final_input' }); // Wait for component to call forge
    } else {
      set({ status: 'awaiting_final_input' });
    }
  },

  forgeFinalAsset: async (details, sessionId) => {
    if (!sessionId) return set({ error: "Session ID missing." });
    
    const { anglesResult, chosenAngle, chosenAssetType } = get();
    if (!anglesResult || !chosenAngle || !chosenAssetType) return set({ error: "Session is missing critical context." });
    
    const angle_data = { ...anglesResult, ...chosenAngle, asset_type: chosenAssetType };
    
    set({ status: 'forging', isRitualRunning: true, error: null });
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/marketing/asset`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, angle_data: angle_data, ...details })
      });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      const { task_id } = await res.json();

      pollProphecy(task_id,
        (result) => set({ status: 'asset_revealed', isRitualRunning: false, finalAsset: result }),
        (error) => set({ status: 'angles_revealed', isRitualRunning: false, error: error.details || error.error })
      );
    } catch (err: any) {
      set({ status: 'angles_revealed', isRitualRunning: false, error: err.message });
    }
  },

  regenerateAsset: () => { console.log("Regeneration needs to be triggered from UI with session ID."); },

  viewDetail: (contentType) => {
    const { finalAsset } = get();
    if (!finalAsset) return;
    let detail: MarketingSagaState['detailedContent'] = null;
    if (contentType === 'html_code' && finalAsset.html_code) detail = { ...finalAsset.html_code, type: 'scroll' };
    else if (contentType === 'deployment_guide' && finalAsset.deployment_guide) detail = { ...finalAsset.deployment_guide, type: 'scroll' };
    else if (contentType === 'image' && finalAsset.image_orb) detail = { title: finalAsset.image_orb.title, content: finalAsset.image_orb.description, type: 'prompt_image' };
    else if (contentType === 'video' && finalAsset.motion_orb) detail = { title: finalAsset.motion_orb.title, content: finalAsset.motion_orb.description, type: 'prompt_video' };
    if (detail) set({ status: 'viewing_detail', detailedContent: detail });
  },

  returnToAsset: () => set({ status: 'asset_revealed', detailedContent: null }),
  
  resetForge: () => {
    set({ status: 'idle', error: null, isRitualRunning: false, productName: null, productDescription: null, targetAudience: null, anglesResult: null, chosenAngle: null, chosenAssetType: null, finalAsset: null, detailedContent: null });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---