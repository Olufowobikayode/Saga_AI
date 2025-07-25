// --- START OF FILE src/store/commerceStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Adding more specific prophecy types for clarity and type safety.
export type CommerceProphecyType = 'Commerce Audit' | 'Arbitrage Paths' | 'Social Selling Saga' | 'Product Route';
export type AuditType = 'Account Audit' | 'Store Audit' | 'Account Prediction';
export type ArbitrageMode = "User_Buys_User_Sells" | "Saga_Buys_User_Sells" | "User_Buys_Saga_Sells" | "Saga_Buys_Saga_Sells";

// SAGA PERSONA: Adding new states for the sub-selection ritual process.
type LedgerStatus =
  | 'idle'
  | 'performing_entry_rite'
  | 'crossroads'
  | 'performing_choice_rite' // The ritual AFTER choosing a main prophecy type.
  | 'awaiting_audit_type'    // The Hall of Scrutiny is unveiled.
  | 'awaiting_arbitrage_mode'// The Hall of Scales is unveiled.
  | 'awaiting_input'
  | 'forging_prophecy'
  | 'prophecy_revealed';

interface CommerceState {
  status: LedgerStatus;
  error: string | null;
  
  chosenProphecyType: CommerceProphecyType | null;
  // NEW: Memory for the specific sub-choices.
  chosenAuditType: AuditType | null;
  chosenArbitrageMode: ArbitrageMode | null;

  lastRequestData: any | null;
  finalProphecy: any | null;

  // The Rites of the Ledger
  enterLedger: () => Promise<void>;
  chooseProphecy: (prophecyType: CommerceProphecyType) => Promise<void>;
  chooseAuditType: (auditType: AuditType) => Promise<void>;
  // We will add chooseArbitrageMode in a later step.
  forgeProphecy: (requestData: any) => Promise<void>;
  regenerateProphecy: () => Promise<void>;
  returnToCrossroads: () => void;
}

const API_BASE_URL = 'http://localhost:8000/api/v10';
const performRitual = () => new Promise(resolve => setTimeout(resolve, 30000));

export const useCommerceStore = create<CommerceState>((set, get) => ({
  status: 'idle',
  error: null,
  chosenProphecyType: null,
  chosenAuditType: null,
  chosenArbitrageMode: null,
  lastRequestData: null,
  finalProphecy: null,

  enterLedger: async () => {
    set({ status: 'performing_entry_rite', error: null });
    await performRitual();
    set({ status: 'crossroads' });
  },

  chooseProphecy: async (prophecyType) => {
    set({ status: 'performing_choice_rite', error: null, chosenProphecyType: prophecyType });
    await performRitual();
    if (prophecyType === 'Commerce Audit') {
      set({ status: 'awaiting_audit_type' });
    } else if (prophecyType === 'Arbitrage Paths') {
      set({ status: 'awaiting_arbitrage_mode' });
    } else {
      set({ status: 'awaiting_input' });
    }
  },

  chooseAuditType: async (auditType) => {
    set({ status: 'performing_choice_rite', error: null, chosenAuditType: auditType });
    await performRitual();
    set({ status: 'awaiting_input' });
  },

  forgeProphecy: async (requestData) => {
    const { chosenProphecyType, chosenAuditType, chosenArbitrageMode } = get();
    if (!chosenProphecyType) return;
    const fullRequestData = { ...requestData, prophecy_type: chosenProphecyType, audit_type: chosenAuditType, mode: chosenArbitrageMode };
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
      set({ status: 'prophecy_revealed', finalProphecy: apiResponse.data });
    } catch (err: any) {
      set({ status: 'awaiting_input', error: err.message || "The Merchant's prophecy could not be forged." });
    }
  },

  regenerateProphecy: async () => {
    const { status, lastRequestData } = get();
    if (status === 'prophecy_revealed' && lastRequestData) {
      await get().forgeProphecy(lastRequestData);
    }
  },

  returnToCrossroads: () => {
    set({
      status: 'crossroads', error: null, chosenProphecyType: null,
      chosenAuditType: null, chosenArbitrageMode: null,
      lastRequestData: null, finalProphecy: null,
    });
  },
}));
// --- END OF FILE src/store/commerceStore.ts ---