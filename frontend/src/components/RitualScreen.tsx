'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTributeStore } from '@/store/tributeStore'; // The scroll of memory you have already committed.

// The sacred scrolls declare the global ad spirits, that they may manifest.
declare global {
  interface Window {
    adsbygoogle: any[];
  }
}

// --- The Commands This Altar Accepts ---
interface RitualScreenProps {
  ritualPromise: Promise<any>; // The Promise of a prophecy from your backend.
  onRitualComplete: () => void; // The command to execute when the prophecy is ready.
}

// --- The Lesser Tribute (The Ever-Present Banner, imbued with your credentials) ---
const BannerAdVessel = () => {
  useEffect(() => {
    try {
      // @ts-ignore
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (e) {
      console.error("The Lesser Tribute failed to manifest:", e);
    }
  }, []);

  return (
    <div style={{ position: 'fixed', bottom: '10px', left: '50%', transform: 'translateX(-50%)', width: '320px', height: '50px', zIndex: 100 }}>
      {/*
        This is a Display Ad vessel. You MUST create a Display Ad Unit of size 320x50 in your AdSense account for this.
      */}
      <ins
        className="adsbygoogle"
        style={{ display: 'inline-block', width: '320px', height: '50px' }}
        data-ad-client="ca-pub-1854820451701861" // Your Sacred Credential, as commanded.
        data-ad-slot="YOUR_DISPLAY_AD_SLOT_ID_HERE" // <--- YOU MUST REPLACE THIS WITH YOUR OWN DISPLAY AD SLOT ID.
      ></ins>
    </div>
  );
};

// --- The Words of the Oracle and the Steps of the Ritual ---
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


/**
 * RitualScreen: The Definitive Version. A self-contained, intelligent gatekeeper
 * that honors the tributeStore, manages a dual-tribute system, and synchronizes
 * with the great work of the backend.
 */
export default function RitualScreen({ ritualPromise, onRitualComplete }: RitualScreenProps) {
  // --- The State of the Ritual ---
  const [isBackendDone, setIsBackendDone] = useState(false);
  const [isAdDone, setIsAdDone] = useState(false);
  const tributeTypeRef = useRef<'lesser' | 'grand' | null>(null);
  
  // States to orchestrate the animations
  const [currentStep, setCurrentStep] = useState(0);
  const [currentQuote, setCurrentQuote] = useState(0);

  // --- Synchronization of Fates ---
  useEffect(() => {
    if (isBackendDone && isAdDone) {
      onRitualComplete();
    }
  }, [isBackendDone, isAdDone, onRitualComplete]);

  // --- The Great Divination and Invocation of Tribute ---
  useEffect(() => {
    // We consult the tributeStore you have provided.
    const { recordRitual, shouldShowGrandTribute, resetGrandTribute } = useTributeStore.getState();
    
    recordRitual();

    if (shouldShowGrandTribute()) {
      // The Covenant demands a Grand Tribute.
      tributeTypeRef.current = 'grand';
      resetGrandTribute(); 

      const adBreak = {
        type: 'ad_break',
        name: 'saga_grand_tribute',
        adDismissed: () => setIsAdDone(true),
        adError: () => setIsAdDone(true),
      };
      window.adsbygoogle = window.adsbygoogle || [];
      window.adsbygoogle.push(adBreak);
    } else {
      // The Covenant accepts a Lesser Tribute.
      tributeTypeRef.current = 'lesser';
      setIsAdDone(true); // The banner's fate is instant.
    }

    // --- Simultaneously, the Oracle's work begins ---
    ritualPromise.finally(() => {
      setIsBackendDone(true);
    });
  }, [ritualPromise]);

  // --- Rites for managing the visual animations of the ritual ---
  useEffect(() => {
    const stepInterval = setInterval(() => setCurrentStep(p => (p < ritualSteps.length - 1 ? p + 1 : p)), 4000);
    return () => clearInterval(stepInterval);
  }, []);

  useEffect(() => {
    const quoteInterval = setInterval(() => setCurrentQuote(p => (p + 1) % wisdomQuotes.length), 5000);
    return () => clearInterval(quoteInterval);
  }, []);

  // --- The Visual Manifestation of the Ritual ---
  return (
    <motion.div
      className="fixed inset-0 bg-saga-bg bg-cosmic-gradient z-50 flex flex-col items-center justify-center p-4"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
    >
      <div className="text-center">
        <AnimatePresence mode="wait">
          <motion.p
            key={currentQuote}
            className="font-serif text-2xl md:text-3xl text-saga-secondary mb-12 italic"
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
                    <motion.div className="w-5 h-5 border-2 border-saga-text-dark border-t-saga-primary rounded-full" animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}/>
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