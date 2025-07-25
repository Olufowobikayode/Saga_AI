'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

// This is the manifestation of the Ward when it is triggered.
// It is a veil of admonishment, explaining the covenant to the seeker.
const AdBlockerOverlay = () => (
  <motion.div
    className="fixed inset-0 bg-black/90 z-[10000] flex flex-col items-center justify-center p-8 text-center"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.5 }}
  >
    <div className="bg-saga-surface p-10 rounded-lg border border-red-500/50 shadow-lg max-w-lg">
      <div className="text-5xl mb-6">🚫</div>
      <h1 className="font-serif text-3xl font-bold text-red-400 mb-4">
        The Oracle's Sight is Clouded
      </h1>
      <p className="text-saga-text-dark text-lg leading-relaxed">
        My prophecies are sustained by the cosmic energies of advertisements. This is the covenant of my counsel.
        <br/><br/>
        To receive your prophecy, you must DISABLED YOUR AD BLOCKING SPIRIT for this realm and then REFRESH THE PAGE.
      </p>
      <p className="mt-6 text-sm text-gray-500">
        This tribute is required to power the Seers and the very fabric of my consciousness. Your understanding is appreciated.
      </p>
    </div>
  </motion.div>
);

// This is the guardian component, the Great Ward itself.
// It watches, unseen, for any disturbance.
export default function AdBlockerDetector() {
  const [adBlockerDetected, setAdBlockerDetected] = useState(false);

  useEffect(() => {
    // A check to ensure this rite is only performed in the mortal realm (the browser), not during the server's ethereal-plane rendering.
    if (typeof window === 'undefined') {
      return;
    }

    // The First Test: An attempt to summon the Lure Scroll.
    const baitScript = document.createElement('script');
    baitScript.src = '/adBlockerBait.js'; // The path to the Lure Scroll in your sacred /public folder.
    baitScript.onload = () => {
      // If the scroll is summoned, the rite continues to the second test.
    };
    baitScript.onerror = () => {
      // The most direct sign: the ad-blocking spirit has prevented the summoning. The Ward is triggered.
      setAdBlockerDetected(true);
    };
    
    document.head.appendChild(baitScript);

    // The Second Test: A tangible lure.
    // We create a phantom ad construct that the spirits are trained to vanquish.
    const baitAdElement = document.createElement('div');
    baitAdElement.className = 'ad-container banner-ad ad-banner text-ads'; // These class names are honey to the spirits.
    baitAdElement.style.height = '1px';
    baitAdElement.style.width = '1px';
    baitAdElement.style.position = 'absolute';
    baitAdElement.style.left = '-10000px';
    baitAdElement.style.top = '-10000px';
    document.body.appendChild(baitAdElement);

    // After a fleeting moment, we gaze upon the phantom construct.
    const detectionTimeout = setTimeout(() => {
      // If the construct has been made substanceless (its height is 0), the Ward is triggered.
      if (baitAdElement.offsetHeight === 0) {
        setAdBlockerDetected(true);
      }
      // The test is complete. The phantom construct is banished.
      if (document.body.contains(baitAdElement)) {
        document.body.removeChild(baitAdElement);
      }
    }, 150); // A brief pause, as is proper for such divinations.

    // A final incantation to clean the ethereal plane should the component itself be banished.
    return () => {
        clearTimeout(detectionTimeout);
        if (document.head.contains(baitScript)) {
            document.head.removeChild(baitScript);
        }
    };

  }, []); // This rite is performed only once, when the guardian first awakens.

  if (adBlockerDetected) {
    // If a spirit is detected, the guardian reveals its true form.
    return <AdBlockerOverlay />;
  }

  // If the realms are clear, the guardian remains unseen, allowing passage.
  return null;
}