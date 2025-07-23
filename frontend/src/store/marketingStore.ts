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
  | 'asset_revealed'    // The final prophecy (the asset) is complete.
  | 'forging_prompt'    // A ritual to unveil a specific visual prompt is in progress.
  | 'prompt_unveiled';  // The visual prompt has been revealed.

// SAGA PERSONA: Defining the structure of the prophecies we will hold.
interface Angle { /* ... */ angle_id: string; title: string; description: string; framework_steps: string[]; }
interface FinalAsset { [key: string]: any; }

// SAGA PERSONA: Defining the full consciousness of the Skald.
interface MarketingSagaState {
  status: ForgeStatus;
  error: string | null;
  
  productName: string | null;
  productDescription: string | null;
  productLink: string | null;

  angles: Angle[];
  chosenAssetType: string | null;
  chosenAngleId: string | null;
  finalAsset: FinalAsset | null;
  
  unveiledPrompt: { // NEW: To hold the data for the PromptUnveiled component
    type: 'Image' | 'Video';
    title: string;
    content: string;
  } | null;
  
  // The sacred rites (functions)
  invokeForge: () => void;
  commandAnvil: (productName: string, productDescription: string, productLink: string) => Promise<void>;
  chooseAssetType: (assetType: string) => void;
  commandScribe: (length: string) => Promise<void>;
  unveilPrompt: (type: 'Image' | 'Video') => Promise<void>; // NEW: A rite to generate a prompt.
  returnToScroll: () => void; // NEW: A rite to go back to the asset display.
  resetForge: () => void;
}

const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const useMarketingStore = create<MarketingSagaState>((set, get) => ({
  // Initial state...
  status: 'idle',
  error: null,
  productName: null,
  productDescription: null,
  productLink: null,
  angles: [],
  chosenAssetType: null,
  chosenAngleId: null,
  finalAsset: null,
  unveiledPrompt: null,

  // Rites...
  invokeForge: () => set({ status: 'awaiting_anvil' }),

  commandAnvil: async (productName, productDescription, productLink) => {
    set({ status: 'forging_angles', error: null });
    // await performRitual();
    const simulatedAngles: Angle[] = [
      { angle_id: 'angle_1', title: "The 'Us vs. Them' Manifesto", description: "...", framework_steps: ["..."] },
      { angle_id: 'angle_2', title: "The Hyper-Specific Problem Solver", description: "...", framework_steps: ["..."] },
    ];
    set({ status: 'angles_revealed', productName, productDescription, productLink, angles: simulatedAngles });
  },

  chooseAssetType: (assetType) => {
    if (['Ad Copy', 'Affiliate Copy', 'Email Copy'].includes(assetType)) {
      set({ status: 'awaiting_scribe', chosenAssetType: assetType });
    } else {
      console.log(`Asset type '${assetType}' does not require length. Forging directly...`);
      // get().commandScribe('Default');
    }
  },

  commandScribe: async (length) => {
    const { angles, chosenAssetType } = get();
    if (!angles || angles.length === 0 || !chosenAssetType) {
      set({ status: 'idle', error: "A critical error occurred. The strategic angle was lost." });
      return;
    }
    const chosenAngle = angles[0];
    set({ status: 'forging_asset', error: null, chosenAngleId: chosenAngle.angle_id });
    // await performRitual();
    const simulatedAsset: FinalAsset = {
      post_text: { title: `${length} ${chosenAssetType}`, content: `This is the final, masterfully crafted ${length.toLowerCase()} ${chosenAssetType.toLowerCase()}...` },
      image_prompt: { title: "Image Prompt for AI", content: "A stunning, photorealistic image of [Your Product] being used by [Your Target Audience] in a [Setting], evoking a feeling of [Emotion]. --ar 16:9" },
      video_prompt: { title: "Video Prompt for AI", content: "A 15-second, cinematic, slow-motion video of [Your Product]. The video starts with a close-up on the product's key feature..." },
    };
    set({ status: 'asset_revealed', finalAsset: simulatedAsset });
  },

  // NEW RITE: This is called when a user clicks "Generate Image/Video Prompt".
  unveilPrompt: async (type) => {
    const { finalAsset } = get();
    if (!finalAsset) return;

    set({ status: 'forging_prompt' });
    console.log(`RITUAL: Unveiling ${type} Prompt...`);
    // await performRitual(); // Placeholder for ad ritual

    const promptKey = type === 'Image' ? 'image_prompt' : 'video_prompt';
    const promptData = finalAsset[promptKey];

    if (promptData) {
      set({
        status: 'prompt_unveiled',
        unveiledPrompt: {
          type: type,
          title: promptData.title,
          content: promptData.content,
        },
      });
    } else {
      set({ status: 'asset_revealed', error: `No ${type} prompt was found in the prophecy.` });
    }
  },

  // NEW RITE: This is called when the user wants to go back from the prompt screen.
  returnToScroll: () => {
    set({ status: 'asset_revealed', unveiledPrompt: null });
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
      unveiledPrompt: null,
    });
  },
}));
// --- END OF FILE src/store/marketingStore.ts ---