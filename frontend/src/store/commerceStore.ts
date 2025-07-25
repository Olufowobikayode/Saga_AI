// --- START OF FILE src/store/commerceStore.ts ---
import { create } from 'zustand';

export type CommerceProphecyType = 'Commerce Audit' | 'Arbitrage Paths' | 'Social Selling Saga' | 'Product Route';
export type AuditType = 'Account Audit' | 'Store Audit' | 'Account Prediction';
export type ArbitrageMode = "User_Buys_User_Sells" | "Saga_Buys_User_Sells" | "User_Buys_Saga_Sells" | "Saga_Buys_Saga_Sells";

type LedgerStatus =
  | 'idle'
  | 'performing_entry_rite'
  | 'crossroads'
  | 'performing_choice_rite'
  | 'awaiting_audit_type'
  | 'awaiting_arbitrage_mode'
  | 'awaiting_input'
  | 'forging_prophecy'
  | 'prophecy_revealed';

interface CommerceState {
  status: LedgerStatus;
  error: string | null;
  ritualPromise: Promise<any> | null;
  
  chosenProphecyType: CommerceProphecyType | null;
  chosenAuditType: AuditType | null;
  chosenArbitrageMode: ArbitrageMode | null;

  lastRequestData: any | null;
  finalProphecy: any | null;

  // The Rites of the Ledger
  enterLedger: () => Promise<void>;
  chooseProphecy: (prophecyType: CommerceProphecyType) => Promise<void>;
  chooseAuditType: (auditType: AuditType) => Promise<void>;
  chooseArbitrageMode: (mode: ArbitrageMode) => Promise<void>;
  forgeProphecy: (requestData: any) => Promise<void>;
  regenerateProphecy: () => Promise<void>;
  returnToCrossroads: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useCommerceStore = create<CommerceState>((set, get) => ({
  status: 'idle', error: null, ritualPromise: null, chosenProphecyType: null, chosenAuditType: null,
  chosenArbitrageMode: null, lastRequestData: null, finalProphecy: null,

  enterLedger: async () => {
    const promise = new Promise(resolve => setTimeout(resolve, 1000));
    set({ status: 'performing_entry_rite', error: null, ritualPromise: promise });
    await promise;
    set({ status: 'crossroads', ritualPromise: null });
  },

  chooseProphecy: async (prophecyType) => {
    const promise = new Promise(resolve => setTimeout(resolve, 1000));
    set({ status: 'performing_choice_rite', error: null, chosenProphecyType: prophecyType, ritualPromise: promise });
    await promise;
    if (prophecyType === 'Commerce Audit') {
      set({ status: 'awaiting_audit_type', ritualPromise: null });
    } else if (prophecyType === 'Arbitrage Paths') {
      set({ status: 'awaiting_arbitrage_mode', ritualPromise: null });
    } else {
      set({ status: 'awaiting_input', ritualPromise: null });
    }
  },

  chooseAuditType: async (auditType) => {
    const promise = new Promise(resolve => setTimeout(resolve, 1000));
    set({ status: 'performing_choice_rite', error: null, chosenAuditType: auditType, ritualPromise: promise });
    await promise;
    set({ status: 'awaiting_input', ritualPromise: null });
  },

  chooseArbitrageMode: async (mode) => {
    const promise = new Promise(resolve => setTimeout(resolve, 1000));
    set({ status: 'performing_choice_rite', error: null, chosenArbitrageMode: mode, ritualPromise: promise });
    await promise;
    set({ status: 'awaiting_input', ritualPromise: null });
  },

  forgeProphecy: async (requestData) => {
    const { chosenProphecyType, chosenAuditType, chosenArbitrageMode } = get();
    if (!chosenProphecyType) return;

    const fullRequestData = { ...requestData, prophecy_type: chosenProphecyType, audit_type: chosenAuditType, mode: chosenArbitrageMode };
    
    const apiCallPromise = fetch(`${API_BASE_URL}/prophesy/commerce`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fullRequestData),
    }).then(async res => {
      if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
      return res.json();
    });

    set({ status: 'forging_prophecy', error: null, lastRequestData: fullRequestData, ritualPromise: apiCallPromise });
    
    try {
      const apiResponse = await apiCallPromise;
      set({ status: 'prophecy_revealed', finalProphecy: apiResponse.data, ritualPromise: null });
    } catch (err: any) {
      set({ status: 'awaiting_input', error: err.message || "The Merchant's prophecy could not be forged.", ritualPromise: null });
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
      status: 'crossroads', error: null, ritualPromise: null, chosenProphecyType: null,
      chosenAuditType: null, chosenArbitrageMode: null,
      lastRequestData: null, finalProphecy: null,
    });
  },
}));
// --- END OF FILE src/store/commerceStore.ts ---