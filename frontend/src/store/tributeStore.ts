import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const TEN_MINUTES_IN_MS = 10 * 60 * 1000;

interface TributeState {
  ritualCount: number;
  lastGrandTributeTimestamp: number;
  recordRitual: () => void;
  shouldShowGrandTribute: () => boolean;
  resetGrandTribute: () => void;
}

export const useTributeStore = create(
  persist<TributeState>(
    (set, get) => ({
      ritualCount: 0,
      lastGrandTributeTimestamp: Date.now(),

      // This rite is called every time a ritual begins
      recordRitual: () => {
        set(state => ({ ritualCount: state.ritualCount + 1 }));
      },

      // The Gatekeeper's Decree
      shouldShowGrandTribute: () => {
        const { ritualCount, lastGrandTributeTimestamp } = get();
        const timeSinceLast = Date.now() - lastGrandTributeTimestamp;
        
        // Logic: Show the interstitial ad if it's the 3rd ritual OR 10 minutes have passed.
        if (ritualCount >= 3 || timeSinceLast > TEN_MINUTES_IN_MS) {
          return true;
        }
        return false;
      },

      // This rite is called after a Grand Tribute is paid, resetting the counters.
      resetGrandTribute: () => {
        set({ ritualCount: 0, lastGrandTributeTimestamp: Date.now() });
      },
    }),
    {
      name: 'saga-tribute-ledger', // The name of the item in localStorage.
    }
  )
);