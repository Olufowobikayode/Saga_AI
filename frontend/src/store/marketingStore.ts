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
  
  // Memory
  productName: string | null;
  productDescription: string | null;
  targetAudience: string | null;

  // Multi-step context
  anglesResult: { marketing_angles: Angle[] } & any | null;
  
  chosenAngle: Angle | null;
  chosenAssetType: string | null;
  
  // Final Result
  finalAsset: FinalAsset | null;
  detailedContent: { title: string; content: string | object; type: 'scroll' | 'prompt_image' | 'prompt_video' } | null;

  // Rites
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, targetAudience: string) => Promise<void>;
  chooseAngleAndAsset: (angleId: string, assetType: string) => Promise<void>;
  forgeFinalAsset: (details: { platform?: string; length?: string; }) => Promise<void>;
  regenerateAsset: () => Promise<void>;
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

  commandAnvil: async (productName, productDescription, targetAudience) => {
    set({ status: 'forging', isRitualRunning: true, error: null });
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/marketing/angles`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_name: productName, product_description: productDescription, target_audience: targetAudience, asset_type: 'Ad Copy' })
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

    // If no more input is needed, forge immediately.
    if (['Affiliate Review'].includes(assetType)) {
      await get().forgeFinalAsset({});
    } else {
      set({ status: 'awaiting_final_input' });
    }
  },

  forgeFinalAsset: async (details) => {
    const { anglesResult, chosenAngle, chosenAssetType } = get();
    if (!anglesResult || !chosenAngle || !chosenAssetType) {
      set({ error: "A critical prophecy session error occurred." });
      return;
    }
    
    // The second task now receives the full context from the first.
    const fullAngleData = {
        ...anglesResult,
        ...chosenAngle,
        asset_type: chosenAssetType,
    };
    
    set({ status: 'forging', isRitualRunning: true, error: null });
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/marketing/asset`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ angle_data: fullAngleData, ...details })
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

  regenerateAsset: async () => {
    // For simplicity, we can have a "last used details" state or just re-trigger with defaults
    await get().forgeFinalAsset({});
  },

  viewDetail: (contentType) => {
    const { finalAsset } = get();
    if (!finalAsset) return;
    
    let detail: MarketingSagaState['detailedContent'] = null;
    if (contentType === 'html_code' && finalAsset.html_code) {
      detail = { ...finalAsset.html_code, type: 'scroll' };
    } else if (contentType === 'deployment_guide' && finalAsset.deployment_guide) {
      detail = { ...finalAsset.deployment_guide, type: 'scroll' };
    } else if (contentType === 'image' && finalAsset.image_orb) {
      detail = { title: finalAsset.image_orb.title, content: finalAsset.image_orb.description, type: 'prompt_image' };
    } else if (contentType === 'video' && finalAsset.motion_orb) {
      detail = { title: finalAsset.motion_orb.title, content: finalAsset.motion_orb.description, type: 'prompt_video' };
    }
    
    if (detail) {
      set({ status: 'viewing_detail', detailedContent: detail });
    }
  },

  returnToAsset: () => set({ status: 'asset_revealed', detailedContent: null }),
  
  resetForge: () => {
    set({
      status: 'idle', error: null, isRitualRunning: false,
      productName: null, productDescription: null, targetAudience: null,
      anglesResult: null, chosenAngle: null, chosenAssetType: null,
      finalAsset: null, detailedContent: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---