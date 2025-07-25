// --- START OF FILE src/store/commerceStore.ts ---
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
export type CommerceProphecyType = 'Commerce Audit' | 'Arbitrage Paths' | 'Social Selling Saga' | 'Product Route';
export type AuditType = 'Account Audit' | 'Store Audit' | 'Account Prediction';
export type ArbitrageMode = "User_Buys_User_Sells" | "Saga_Buys_User_Sells" | "User_Buys_Saga_Sells" | "Saga_Buys_Saga_Sells";

type LedgerStatus = 'idle' | 'crossroads' | 'awaiting_sub_choice' | 'awaiting_input' | 'forging' | 'prophecy_revealed';

interface CommerceState {
  status: LedgerStatus;
  error: string | null;
  isRitualRunning: boolean;
  
  // Memory
  chosenProphecyType: CommerceProphecyType | null;
  chosenAuditType: AuditType | null;
  chosenArbitrageMode: ArbitrageMode | null;
  lastRequestData: any | null;
  finalProphecy: any | null;

  // Rites of the Ledger
  enterLedger: () => void;
  chooseProphecy: (prophecyType: CommerceProphecyType) => void;
  chooseSubChoice: (choice: AuditType | ArbitrageMode) => void;
  forgeProphecy: (requestData: any) => Promise<void>;
  regenerateProphecy: () => Promise<void>;
  returnToCrossroads: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useCommerceStore = create<CommerceState>((set, get) => ({
  status: 'idle', error: null, isRitualRunning: false,
  chosenProphecyType: null, chosenAuditType: null, chosenArbitrageMode: null,
  lastRequestData: null, finalProphecy: null,

  enterLedger: () => set({ status: 'crossroads' }),

  chooseProphecy: (prophecyType) => {
    set({ chosenProphecyType: prophecyType, chosenAuditType: null, chosenArbitrageMode: null });
    if (prophecyType === 'Commerce Audit' || prophecyType === 'Arbitrage Paths') {
      set({ status: 'awaiting_sub_choice' });
    } else {
      set({ status: 'awaiting_input' });
    }
  },

  chooseSubChoice: (choice) => {
    if (get().chosenProphecyType === 'Commerce Audit') {
      set({ chosenAuditType: choice as AuditType, status: 'awaiting_input' });
    } else if (get().chosenProphecyType === 'Arbitrage Paths') {
      set({ chosenArbitrageMode: choice as ArbitrageMode, status: 'awaiting_input' });
    }
  },

  forgeProphecy: async (requestData) => {
    const { chosenProphecyType, chosenAuditType, chosenArbitrageMode } = get();
    if (!chosenProphecyType) return;

    const fullRequestData = { ...requestData, prophecy_type: chosenProphecyType, audit_type: chosenAuditType, mode: chosenArbitrageMode };
    set({ status: 'forging', isRitualRunning: true, error: null, lastRequestData: fullRequestData });
    
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/commerce`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fullRequestData),
      });
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      const { task_id } = await res.json();

      pollProphecy(task_id,
        (result) => set({ status: 'prophecy_revealed', isRitualRunning: false, finalProphecy: result }),
        (error) => set({ status: 'awaiting_input', isRitualRunning: false, error: error.details || error.error })
      );
    } catch (err: any) {
      set({ status: 'awaiting_input', isRitualRunning: false, error: err.message });
    }
  },

  regenerateProphecy: async () => {
    const { lastRequestData } = get();
    if (lastRequestData) {
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