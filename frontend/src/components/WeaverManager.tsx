// --- START OF FILE frontend/src/components/WeaverManager.tsx ---
'use client';

import React from 'react';
import { useContentStore } from '@/store/contentStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import SparkForm from './SparkForm';
import HallOfSparks from './HallOfSparks';
import WeaversCrossroads from './WeaversCrossroads';
import ToneChamber from './ToneChamber';
import RealmChamber from './RealmChamber';
import LoomScribesChamber from './LoomScribesChamber';
import EchoChamber from './EchoChamber';
import FinalContentScroll from './FinalContentScroll';

/**
 * WeaverManager: The master controller for the entire Content Saga workflow.
 * It reads the status from the contentStore and renders the appropriate UI.
 */
export default function WeaverManager() {
  const status = useContentStore((state) => state.status);
  const ritualPromise = useContentStore((state) => state.ritualPromise);

  const handleRitualComplete = () => {
    console.log("WeaverManager acknowledges ritual completion.");
    // The store manages its own state transitions upon promise resolution.
  };

  const renderCurrentStage = () => {
    switch (status) {
      // Spark Generation Path
      case 'awaiting_spark_topic':
        return <SparkForm />;
      case 'sparks_revealed':
        return <HallOfSparks />;
      case 'crossroads_revealed':
        return <WeaversCrossroads />;

      // Social Post Path
      case 'awaiting_tone':
        return <ToneChamber />;
      case 'awaiting_realm':
        return <RealmChamber />;
      case 'awaiting_length':
        return <LoomScribesChamber />;
      case 'social_post_woven':
        return <FinalContentScroll />;
      
      // Comment Path
      case 'awaiting_echo':
        return <EchoChamber />;
      case 'comment_woven':
        return <FinalContentScroll />;

      // Blog Post Path
      case 'blog_woven':
        return <FinalContentScroll />;

      // Ritual states
      case 'weaving_sparks':
      case 'weaving_social_post':
      case 'weaving_comment':
      case 'weaving_blog':
        // CORRECTED: Pass the required props to RitualScreen
        return (
          <RitualScreen
            key={`weaver-ritual-${status}`}
            ritualPromise={ritualPromise}
            onRitualComplete={handleRitualComplete}
          />
        );

      // Default/Idle State
      default:
        return <div className="text-center p-8">Preparing the Weaver's Loom...</div>;
    }
  };

  return (
    <div>
      <AnimatePresence mode="wait">
        {renderCurrentStage()}
      </AnimatePresence>
    </div>
  );
}
// --- END OF FILE frontend/src/components/WeaverManager.tsx ---