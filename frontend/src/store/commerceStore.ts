// --- START OF REFACTORED FILE frontend/src/store/commerceStore.ts ---
import { create } from 'zustand';

// --- Polling Helper ---
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
  }, 4000);
};

// --- State Types ---
export type CommerceProphecyType = 'Commerce Audit' | 'Arbitrage Paths' | 'Social Selling Saga' | 'Product Route';
export type AuditType = 'Account Audit' | 'Store Audit' | 'Account Prediction';
export type ArbitrageMode = "User_Buys_User_Sells" | "Saga_Buys_User_Sells" | "User_Buys_Saga_Sells" | "Saga_Buys_Saga_Sells";

type LedgerStatus = 'idle' | 'crossroads' | 'awaiting_audit_type' | 'awaiting_arbitrage_mode' | 'awaiting_input' | 'forging_prophecy' | 'prophecy_revealed';

interface CommerceState {
  status: LedgerStatus;
  error: string | null;
  ritualPromise: Promise<any> | null;
  
  chosenProphecyType: CommerceProphecyType | null;
  chosenAuditType: AuditType | null;
  chosenArbitrageMode: ArbitrageMode | null;
  lastRequestData: any | null;
  finalProphecy: any | null;

  // Rites of the Ledger
  enterLedger: () => void;
  chooseProphecy: (prophecyType: CommerceProphecyType) => void;
  chooseAuditType: (auditType: AuditType) => void;
  chooseArbitrageMode: (arbitrageMode: ArbitrageMode) => void;
  forgeProphecy: (requestData: any, sessionId: string) => void;
  regenerateProphecy: (sessionId: string) => void;
  returnToCrossroads: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useCommerceStore = create<CommerceState>((set, get) => ({
  status: 'idle', error: null, ritualPromise: null,
  chosenProphecyType: null, chosenAuditType: null, chosenArbitrageMode: null,
  lastRequestData: null, finalProphecy: null,

  enterLedger: () => set({ status: 'crossroads' }),

  chooseProphecy: (prophecyType) => {
    set({ chosenProphecyType: prophecyType, chosenAuditType: null, chosenArbitrageMode: null });
    if (prophecyType === 'Commerce Audit') {
      set({ status: 'awaiting_audit_type' });
    } else if (prophecyType === 'Arbitrage Paths') {
      set({ status: 'awaiting_arbitrage_mode' });
    } else {
      set({ status: 'awaiting_input' });
    }
  },

  chooseAuditType: (auditType) => set({ chosenAuditType: auditType, status: 'awaiting_input' }),
  chooseArbitrageMode: (arbitrageMode) => set({ chosenArbitrageMode: arbitrageMode, status: 'awaiting_input' }),

  forgeProphecy: (requestData, sessionId) => {
    if (!sessionId) return set({ error: "Session ID missing." });

    const { chosenProphecyType, chosenAuditType, chosenArbitrageMode } = get();
    if (!chosenProphecyType) return;

    const fullRequestData = { session_id: sessionId, ...requestData, prophecy_type: chosenProphecyType, audit_type: chosenAuditType, mode: chosenArbitrageMode };
    set({ status: 'forging_prophecy', error: null, lastRequestData: fullRequestData });
    
    const promise = new Promise(async (resolve, reject) => {
        try {
            const res = await fetch(`${API_BASE_URL}/prophesy/commerce`, {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(fullRequestData),
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
            const { task_id } = await res.json();
      
            pollProphecy(task_id,
              (result) => {
                set({ status: 'prophecy_revealed', finalProphecy: result });
                resolve(result);
              },
              (error) => {
                const msg = error.details || error.error;
                set({ status: 'awaiting_input', error: msg });
                reject(new Error(msg));
              }
            );
        } catch (err: any) {
            set({ status: 'awaiting_input', error: err.message });
            reject(err);
        }
    });

    set({ ritualPromise: promise });
  },

  regenerateProphecy: (sessionId) => {
    const { lastRequestData } = get();
    if (lastRequestData) {
      // We only need the requestData part, not the session_id from the last request
      const { session_id, ...pureRequestData } = lastRequestData;
      get().forgeProphecy(pureRequestData, sessionId);
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
// --- END OF REFACTORED FILE frontend/src/store/commerceStore.ts ---