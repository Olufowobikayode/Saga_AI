// --- START OF FILE src/components/WeaverManager.tsx ---
'use client';

import React from 'react';
import { useContentStore } from '@/store/contentStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import SparkForm from './SparkForm';
import HallOfSparks from './HallOfSparks';
import WeaversCrossroads from './WeaversCrossroads';
import ToneChamber from './ToneChamber'; // Summoning the real Tone Chamber.

// We will create these new components in the upcoming steps.
// For now, they are placeholders.
const RealmChamber = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for RealmChamber</div>;
const ScribesChamber = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for ScribesChamber</div>;
const EchoChamber = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for EchoChamber</div>;
const FinalContentScroll = () => <div className="p-8 bg-saga-surface rounded-lg">Placeholder for FinalContentScroll</div>;


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
        // Now rendering the real component instead of the placeholder.
        return <ToneChamber />;
      case 'awaiting_realm':
        return <RealmChamber />;
      case 'awaiting_length':
        return <ScribesChamber />;
      case 'weaving_social_post':
        return <RitualScreen />;
      case 'social_post_woven':
        return <FinalContentScroll />;
      
      // Comment Path
      case 'awaiting_echo':
        return <EchoChamber />;
      case 'weaving_comment':
        return <RitualScreen />;
      case 'comment_woven':
        return <FinalContentScroll />;

      // Blog Post Path
      case 'weaving_blog':
        return <RitualScreen />;
      case 'blog_woven':
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