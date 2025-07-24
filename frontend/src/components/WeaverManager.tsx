// --- START OF FILE src/components/WeaverManager.tsx ---
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
import FinalContentScroll from './FinalContentScroll'; // Summoning the real Final Scroll.

/**
 * WeaverManager: The master controller for the entire Content Saga workflow.
 * It reads the status from the contentStore and renders the appropriate UI.
 */
export default function WeaverManager() {
  const status = useContentStore((state) => state.status);

  const renderCurrentStage = () => {
    switch (status) {
      // Spark Generation Path
      case 'awaiting_spark_topic':
        return <SparkForm />;
      case 'weaving_sparks':
        return <RitualScreen />;
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
      case 'weaving_social_post':
        return <RitualScreen />;
      case 'social_post_woven':
        // Now rendering the real component instead of the placeholder.
        return <FinalContentScroll />;
      
      // Comment Path
      case 'awaiting_echo':
        return <EchoChamber />;
      case 'weaving_comment':
        return <RitualScreen />;
      case 'comment_woven':
        // Now rendering the real component instead of the placeholder.
        return <FinalContentScroll />;

      // Blog Post Path
      case 'weaving_blog':
        return <RitualScreen />;
      case 'blog_woven':
        // Now rendering the real component instead of the placeholder.
        return <FinalContentScroll />;

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
// --- END OF FILE src/components/WeaverManager.tsx ---