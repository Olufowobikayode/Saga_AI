// --- START OF REFACTORED FILE frontend/src/components/RitualScreen.tsx ---
'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTributeStore } from '@/store/tributeStore';

declare global {
  interface Window {
    adsbygoogle: any[];
  }
}

// --- CONFIGURATION ---
const MINIMUM_RITUAL_DURATION_MS = 5000; // 5 seconds

// A placeholder. In a real app, you would have different slots.
const DISPLAY_AD_SLOT_ID = "3987431269"; 

// --- BANNER AD COMPONENT ---
const BannerAdVessel = () => {
  useEffect(() => {
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (e) {
      console.error("The Lesser Tribute (Banner Ad) failed to manifest:", e);
    }
  }, []);

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 w-[320px] h-[50px] z-[100] bg-saga-surface/50">
      <ins
        className="adsbygoogle"
        style={{ display: 'inline-block', width: '320px', height: '50px' }}
        data-ad-client="ca-pub-1854820451701861"
        data-ad-slot={DISPLAY_AD_SLOT_ID} 
      ></ins>
    </div>
  );
};

// --- DATA FOR ANIMATIONS ---
const wisdomQuotes = [
  "A strategy without data is merely a wish upon a dying star.",
  "The whispers of the market are the true winds of fortune.",
  "Victory is not seized; it is meticulously forged in the fires of preparation.",
  "Do not chase the fleeting trend. Understand the eternal need that drives it.",
  "Foresight is the art of seeing the inevitable before it occurs."
];

const ritualSteps = [
  "Dispatching Seers to the Digital Realms...",
  "Reading the Runes of the Cosmic Chorus...",
  "Weaving the Quantum Threads of Fate...",
  "Synchronizing the Tributes of Mortals...",
  "Deciphering the Oracle's Final Prophecy..."
];

// --- COMPONENT PROPS ---
interface RitualScreenProps {
  ritualPromise: Promise<any> | null;
  onRitualComplete: () => void;
}

/**
 * RitualScreen: The Definitive Version. A self-contained, intelligent gatekeeper
 * that honors the tributeStore, manages a dual-tribute system, and synchronizes
 * with the great work of the backend by consuming a promise from the store.
 */
export default function RitualScreen({ ritualPromise, onRitualComplete }: RitualScreenProps) {
  const [isBackendDone, setIsBackendDone] = useState(false);
  const [isAdDone, setIsAdDone] = useState(false);
  const [isMinTimeDone, setIsMinTimeDone] = useState(false);
  const tributeTypeRef = useRef<'lesser' | 'grand' | null>(null);

  const [currentStep, setCurrentStep] = useState(0);
  const [currentQuote, setCurrentQuote] = useState(0);

  // --- SYNCHRONIZATION OF FATES ---
  useEffect(() => {
    if (isBackendDone && isAdDone && isMinTimeDone) {
      onRitualComplete();
    }
  }, [isBackendDone, isAdDone, isMinTimeDone, onRitualComplete]);

  // --- THE GREAT DIVINATION & RITUAL INVOCATION ---
  useEffect(() => {
    // 1. Minimum UX Timer
    const minTimeTimeout = setTimeout(() => setIsMinTimeDone(true), MINIMUM_RITUAL_DURATION_MS);

    // 2. Ad Tribute Logic
    const { recordRitual, shouldShowGrandTribute, resetGrandTribute } = useTributeStore.getState();
    recordRitual();

    if (shouldShowGrandTribute()) {
      tributeTypeRef.current = 'grand';
      resetGrandTribute();
      try {
        const adBreak = {
          type: 'ad_break',
          name: 'saga_grand_tribute', // A name for this ad break placement
          adDismissed: () => { console.log('Ad dismissed'); setIsAdDone(true); },
          adError: (e: any) => { console.error('Ad error:', e.error); setIsAdDone(true); },
          adBreakDone: (placementInfo: any) => {
             console.log('Ad break done:', placementInfo.breakStatus);
             setIsAdDone(true);
          },
        };
        (window.adsbygoogle = window.adsbygoogle || []).push(adBreak);
      } catch (e) {
        console.error("The Grand Tribute (Interstitial) failed to manifest:", e);
        setIsAdDone(true); // Fail open to not block user
      }
    } else {
      tributeTypeRef.current = 'lesser';
      setIsAdDone(true); // Banner ad doesn't block, so it's considered "done" instantly
    }

    // 3. Backend Prophecy Logic
    if (ritualPromise) {
      ritualPromise
        .catch(err => {
          console.error("The backend prophecy ritual failed:", err);
          // The store handles setting the error state. This screen's job is just to finish.
        })
        .finally(() => {
          setIsBackendDone(true);
        });
    } else {
      console.error("RitualScreen was summoned without a ritualPromise.");
      setIsBackendDone(true); // Fail open if no promise was provided
    }

    // Cleanup
    return () => {
      clearTimeout(minTimeTimeout);
    };
  }, [ritualPromise]);

  // --- Rites for managing the visual animations of the ritual ---
  useEffect(() => {
    const stepInterval = setInterval(() => setCurrentStep(p => (p < ritualSteps.length - 1 ? p + 1 : p)), 4000);
    const quoteInterval = setInterval(() => setCurrentQuote(p => (p + 1) % wisdomQuotes.length), 5000);
    return () => {
      clearInterval(stepInterval);
      clearInterval(quoteInterval);
    };
  }, []);

  return (
    <motion.div
      className="fixed inset-0 bg-saga-bg bg-cosmic-gradient z-50 flex flex-col items-center justify-center p-4"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
    >
      <div className="text-center">
        <AnimatePresence mode="wait">
          <motion.p
            key={currentQuote}
            className="font-serif text-2xl md:text-3xl text-saga-secondary mb-12 italic max-w-2xl"
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.8 }}
          >
            "{wisdomQuotes[currentQuote]}"
          </motion.p>
        </AnimatePresence>
        <div className="space-y-4 max-w-md mx-auto">
          {ritualSteps.map((step, index) => (
            <motion.div key={step} className="flex items-center text-lg" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: index * 0.2 }}>
              <div className="w-8 h-8 mr-4 flex items-center justify-center">
                <AnimatePresence>
                  {index < currentStep ? (
                    <motion.svg initial={{ scale: 0 }} animate={{ scale: 1 }} className="w-6 h-6 text-saga-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </motion.svg>
                  ) : (
                    index === currentStep && <motion.div className="w-5 h-5 border-2 border-saga-text-dark border-t-saga-primary rounded-full" animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}/>
                  )}
                </AnimatePresence>
              </div>
              <span className={index <= currentStep ? "text-saga-text-light" : "text-saga-text-dark"}>{step}</span>
            </motion.div>
          ))}
        </div>
      </div>
      {tributeTypeRef.current === 'lesser' && <BannerAdVessel />}
    </motion.div>
  );
}
// --- END OF REFACTORED FILE frontend/src/components/RitualScreen.tsx ---