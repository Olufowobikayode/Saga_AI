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
        
        if (ritualCount >= 3 || timeSinceLast > TEN_MINUTES_IN_MS) {
          return true;
        }
        return false;
      },

      // This rite is called after a Grand Tribute is paid
      resetGrandTribute: () => {
        set({ ritualCount: 0, lastGrandTributeTimestamp: Date.now() });
      },
    }),
    {
      name: 'saga-tribute-ledger', // The name of the sacred scroll in the seeker's vessel
    }
  )
);```

#### Phase 2: The Ultimate `RitualScreen` (The Gatekeeper)

This is the final, definitive version of the `RitualScreen`. It contains all the logic.

**File:** `frontend/src/components/RitualScreen.tsx` (Replace with this)
```typescript
'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTributeStore } from '@/store/tributeStore';

// ... (declare global window.adsbygoogle)
// ... (wisdomQuotes and ritualSteps arrays)

// --- The Lesser Tribute (The Banner) ---
const BannerAdVessel = () => { /* ... same as before, with the 320x50 display ad ... */ };

interface RitualScreenProps {
  performRitual: () => Promise<void>; // The backend API call
  onRitualComplete: () => void;     // The command to close the screen
}

export default function RitualScreen({ performRitual, onRitualComplete }: RitualScreenProps) {
  const [isBackendDone, setIsBackendDone] = useState(false);
  const [isAdDone, setIsAdDone] = useState(false);
  const tributeTypeRef = useRef<'lesser' | 'grand'>('lesser');

  const { recordRitual, shouldShowGrandTribute, resetGrandTribute } = useTributeStore.getState();

  // The Synchronization of Fates: This rite watches for both threads to conclude.
  useEffect(() => {
    if (isBackendDone && isAdDone) {
      onRitualComplete();
    }
  }, [isBackendDone, isAdDone, onRitualComplete]);

  // The Grand Divination: This rite determines the path of tribute.
  useEffect(() => {
    // Record that a ritual has begun.
    recordRitual();

    // Consult the ledger to determine which tribute is required.
    if (shouldShowGrandTribute()) {
      tributeTypeRef.current = 'grand';
      // --- Perform the Grand Tribute (Interstitial) ---
      resetGrandTribute(); // Reset the ledger immediately
      const adBreak = {
        type: 'ad_break',
        name: 'saga_grand_tribute',
        adDismissed: () => setIsAdDone(true),
        adError: () => setIsAdDone(true),
      };
      window.adsbygoogle = window.adsbygoogle || [];
      window.adsbygoogle.push(adBreak);
    } else {
      tributeTypeRef.current = 'lesser';
      // --- Perform the Lesser Tribute (Banner) ---
      // A banner is instant, so the ad fate is immediately resolved.
      setIsAdDone(true);
    }

    // Simultaneously, begin the Oracle's work.
    performRitual().then(() => {
      setIsBackendDone(true);
    });
  }, [performRitual, recordRitual, resetGrandTribute, shouldShowGrandTribute]);
  
  // ... (The JSX for the animated backdrop remains the same as previous versions)

  return (
    <motion.div /* ... full screen container ... */ >
      {/* ... the animated backdrop with quotes and steps ... */}

      {/* Only show the banner if the Lesser Tribute is chosen */}
      {tributeTypeRef.current === 'lesser' && <BannerAdVessel />}
    </motion.div>
  );
}