// --- START OF FILE src/store/marketingStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Defining the stages of the Skald's Forge ritual.
type ForgeStatus =
  | 'idle'              // The Forge is quiet, awaiting a command.
  | 'awaiting_anvil'    // The entry ritual is complete, awaiting the user's core input.
  | 'forging_angles'    // The ritual to forge strategic angles is in progress.
  | 'angles_revealed'   // The strategic angles are forged and await the user's choice.
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
  // This will hold the final generated content, e.g., ad copy, HTML code, etc.
  [key: string]: any;
}

// SAGA PERSONA: Defining the full consciousness of the Skald.
interface MarketingSagaState {
  status: ForgeStatus;
  error: string | null;
  
  // The user's initial command
  productName: string | null;
  productDescription: string | null;
  productLink: string | null;

  // The prophecies revealed
  angles: Angle[];
  chosenAngleId: string | null;
  finalAsset: FinalAsset | null;
  
  // The sacred rites (functions)
  invokeForge: () => void; // The entry ritual
  commandAnvil: (productName: string, productDescription: string, productLink: string) => Promise<void>; // Submits the core input
  chooseAngle: (angleId: string, assetType: string) => Promise<void>; // Chooses an angle to forge an asset
  resetForge: () => void; // Resets the forge for a new prophecy
}

// A placeholder for the 30-second ad ritual
const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const useMarketingStore = create<MarketingSagaState>((set, get) => ({
  // Initial state of the Forge
  status: 'idle',
  error: null,
  productName: null,
  productDescription: null,
  productLink: null,
  angles: [],
  chosenAngleId: null,
  finalAsset: null,

  // --- THE SACRED RITES ---

  invokeForge: () => {
    // This is called when the user first enters the Forge.
    // For now, it just sets the status, but we will add the ritual later.
    set({ status: 'awaiting_anvil' });
  },

  commandAnvil: async (productName, productDescription, productLink) => {
    set({ status: 'forging_angles', error: null });
    
    // Here we would perform the ritual (ad timer) and API call in parallel.
    // For now, we'll simulate it.
    console.log("RITUAL: Forging marketing angles...");
    // await performRitual(); // This will be uncommented later.

    // SAGA LOGIC: This is where we would call the backend's `prophesy_marketing_angles`.
    // We will simulate a successful response for now.
    const simulatedAngles: Angle[] = [
      { angle_id: 'angle_1', title: "The 'Us vs. Them' Manifesto", description: "...", framework_steps: ["..."] },
      { angle_id: 'angle_2', title: "The Hyper-Specific Problem Solver", description: "...", framework_steps: ["..."] },
      { angle_id: 'angle_3', title: "The Aspirational Identity", description: "...", framework_steps: ["..."] },
    ];

    set({
      status: 'angles_revealed',
      productName,
      productDescription,
      productLink,
      angles: simulatedAngles,
    });
  },

  chooseAngle: async (angleId, assetType) => {
    set({ status: 'forging_asset', error: null, chosenAngleId: angleId });

    console.log(`RITUAL: Forging asset of type '${assetType}' using angle '${angleId}'...`);
    // await performRitual(); // This will be uncommented later.

    // SAGA LOGIC: This is where we would call the backend's asset generation endpoint.
    // We will simulate a successful response.
    const simulatedAsset: FinalAsset = {
      post_text: { title: "Ad Copy", content: "This is the final, masterfully crafted ad copy..." },
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
      chosenAngleId: null,
      finalAsset: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---