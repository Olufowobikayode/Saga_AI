// --- START OF FILE src/store/commerceStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Defining the four great prophecies of the Merchant.
export type CommerceProphecyType = 'Commerce Audit' | 'Arbitrage Paths' | 'Social Selling Saga' | 'Product Route';

// SAGA PERSONA: Defining the stages of the Merchant's prophecy.
type LedgerStatus =
  | 'idle'              // The Ledger is closed.
  | 'performing_entry_rite' // The ritual upon entering the hall.
  | 'crossroads'        // Awaiting the user's choice of which prophecy to pursue.
  | 'awaiting_input'    // Awaiting the user's input for their chosen prophecy.
  | 'forging_prophecy'  // The ritual to generate the prophecy is in progress.
  | 'prophecy_revealed';// The final prophecy is ready.

// SAGA PERSONA: Defining the full consciousness of the Merchant.
interface CommerceState {
  status: LedgerStatus;
  error: string | null;
  
  // Memory of the Merchant
  chosenProphecyType: CommerceProphecyType | null;
  lastRequestData: any | null; // To store the data for regeneration.
  finalProphecy: any | null;

  // The Rites of the Ledger
  enterLedger: () => Promise<void>;
  chooseProphecy: (prophecyType: CommerceProphecyType) => Promise<void>;
  forgeProphecy: (requestData: any) => Promise<void>;
  regenerateProphecy: () => Promise<void>;
  returnToCrossroads: () => void;
}

const API_BASE_URL = 'http://localhost:8000/api/v10';
const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const useCommerceStore = create<CommerceState>((set, get) => ({
  // --- Initial State ---
  status: 'idle',
  error: null,
  chosenProphecyType: null,
  lastRequestData: null,
  finalProphecy: null,

  // --- The Rites ---
  enterLedger: async () => {
    set({ status: 'performing_entry_rite', error: null });
    await performRitual();
    set({ status: 'crossroads' });
  },

  chooseProphecy: async (prophecyType) => {
    // A ritual must be observed when a path is chosen.
    set({ status: 'forging_prophecy', error: null }); // Use the main forging status for intermediate rituals
    await performRitual();
    set({ status: 'awaiting_input', chosenProphecyType: prophecyType });
  },

  forgeProphecy: async (requestData) => {
    const prophecyType = get().chosenProphecyType;
    if (!prophecyType) return;

    // The request data from the form must include the prophecy_type for the backend.
    const fullRequestData = { ...requestData, prophecy_type: prophecyType };

    set({ status: 'forging_prophecy', error: null, lastRequestData: fullRequestData });
    
    try {
      const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/commerce`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fullRequestData),
      }).then(async res => {
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
        return res.json();
      });

      const [apiResponse] = await Promise.all([apiCallPromise, performRitual()]);

      set({
        status: 'prophecy_revealed',
        finalProphecy: apiResponse.data,
      });
    } catch (err: any) {
      set({ status: 'awaiting_input', error: err.message || "The Merchant's prophecy could not be forged." });
    }
  },

  regenerateProphecy: async () => {
    const { status, lastRequestData } = get();
    if (status === 'prophecy_revealed' && lastRequestData) {
      // Re-run the final forging ritual with the last known data.
      await get().forgeProphecy(lastRequestData);
    }
  },

  returnToCrossroads: () => {
    set({
      status: 'crossroads',
      error: null,
      chosenProphecyType: null,
      lastRequestData: null,
      finalProphecy: null,
    });
  },
}));
// --- END OF FILE src/store/commerceStore.ts ---