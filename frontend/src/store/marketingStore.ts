// --- START OF FILE src/store/marketingStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Defining the stages of the Skald's Forge ritual.
type ForgeStatus =
  | 'idle'              // The Forge is quiet, awaiting a command.
  | 'awaiting_anvil'    // The entry ritual is complete, awaiting the user's core input.
  | 'forging_angles'    // The ritual to forge strategic angles is in progress.
  | 'angles_revealed'   // The strategic angles are forged and await the user's choice of ASSET TYPE.
  | 'awaiting_scribe'   // An asset type has been chosen, awaiting the user's choice of LENGTH.
  | 'forging_asset'     // The final ritual to forge a specific asset is in progress.
  | 'asset_revealed';   // The final prophecy (the asset) is complete.

// SAGA PERSONA: Defining the structure of the prophecies we will hold.
interface Angle {
  angle_id: string;
  title: string;
  description: string;
  framework_steps: string[];
}

interface FinalAsset {
  [key: string]: any;
}

// SAGA PERSONA: Defining the full consciousness of the Skald.
interface MarketingSagaState {
  status: ForgeStatus;
  error: string | null;
  
  productName: string | null;
  productDescription: string | null;
  productLink: string | null;

  angles: Angle[];
  chosenAssetType: string | null; // NEW: Remember which asset type was chosen.
  chosenAngleId: string | null;
  finalAsset: FinalAsset | null;
  
  // The sacred rites (functions)
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, productLink: string) => Promise<void>;
  chooseAssetType: (assetType: string) => void; // NEW: A rite to choose the asset type.
  commandScribe: (length: string) => Promise<void>; // NEW: A rite to choose the length and forge the final asset.
  resetForge: () => void;
}

const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const useMarketingStore = create<MarketingSagaState>((set, get) => ({
  status: 'idle',
  error: null,
  productName: null,
  productDescription: null,
  productLink: null,
  angles: [],
  chosenAssetType: null,
  chosenAngleId: null,
  finalAsset: null,

  invokeForge: () => {
    set({ status: 'awaiting_anvil' });
  },

  commandAnvil: async (productName, productDescription, productLink) => {
    set({ status: 'forging_angles', error: null });
    // await performRitual(); // Placeholder for ad ritual
    const simulatedAngles: Angle[] = [
      { angle_id: 'angle_1', title: "The 'Us vs. Them' Manifesto", description: "...", framework_steps: ["..."] },
      { angle_id: 'angle_2', title: "The Hyper-Specific Problem Solver", description: "...", framework_steps: ["..."] },
    ];
    set({
      status: 'angles_revealed',
      productName,
      productDescription,
      productLink,
      angles: simulatedAngles,
    });
  },

  // NEW RITE: This is called when a user clicks a card in the Hall of Angles.
  chooseAssetType: (assetType) => {
    // For assets like Ad Copy, we need to ask for the length.
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) {
      set({ status: 'awaiting_scribe', chosenAssetType: assetType });
    } else {
      // For assets like Funnels or Reviews, we can forge them directly.
      // We will implement this logic later. For now, we just log it.
      console.log(`Asset type '${assetType}' does not require length. Forging directly...`);
      // get().commandScribe('Default'); // Example of direct forging
    }
  },

  // NEW RITE: This is called when a user clicks a card in the Scribe's Chamber.
  commandScribe: async (length) => {
    const { angles, chosenAssetType } = get();
    if (!angles || angles.length === 0 || !chosenAssetType) {
      set({ status: 'idle', error: "A critical error occurred. The strategic angle was lost." });
      return;
    }
    
    // For now, we'll just pick the first strategic angle returned by the backend.
    // A more advanced UI could let the user choose from the 3-4 angles.
    const chosenAngle = angles[0];

    set({ status: 'forging_asset', error: null, chosenAngleId: chosenAngle.angle_id });
    
    console.log(`RITUAL: Forging ${length} ${chosenAssetType} using angle '${chosenAngle.title}'...`);
    // await performRitual(); // Placeholder for ad ritual

    const simulatedAsset: FinalAsset = {
      post_text: { title: `${length} ${chosenAssetType}`, content: `This is the final, masterfully crafted ${length.toLowerCase()} ${chosenAssetType.toLowerCase()}...` },
      image_prompt: { title: "Image Prompt", content: "A photorealistic image of..." },
      video_prompt: { title: "Video Prompt", content: "A 15-second video showing..." },
    };

    set({
      status: 'asset_revealed',
      finalAsset: simulatedAsset,
    });
  },

  resetForge: () => {
    set({
      status: 'idle',
      error: null,
      productName: null,
      productDescription: null,
      productLink: null,
      angles: [],
      chosenAssetType: null,
      chosenAngleId: null,
      finalAsset: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---