// --- START OF FILE frontend/src/components/ForgeManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useMarketingStore } from '@/store/marketingStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import AnvilForm from './AnvilForm';
import HallOfAngles from './HallOfAngles';
import ScribesChamber from './ScribesChamber';
import PlatformChamber from './PlatformChamber';
import TextPlatformChamber from './TextPlatformChamber';
import FinalScroll from './FinalScroll';
import PromptUnveiled from './PromptUnveiled';
import ScrollUnfurled from './ScrollUnfurled';

/**
 * ForgeManager: The master controller for the entire Skald's Forge workflow.
 * It reads the status from the marketingStore and renders the appropriate UI.
 */
export default function ForgeManager() {
  const { 
    status, 
    invokeForge, 
    unveiledPrompt,
    unfurledContent,
    returnToScroll,
    ritualPromise // Summoning the promise from the store
  } = useMarketingStore();

  useEffect(() => {
    if (status === 'idle') {
      invokeForge();
    }
  }, [status, invokeForge]);

  const handleRitualComplete = () => {
    // The store handles state transitions upon promise resolution, so this can be a no-op.
    console.log("ForgeManager acknowledges ritual completion.");
  };

  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_anvil':
        return <AnvilForm />;
      
      case 'angles_revealed':
        return <HallOfAngles />;

      case 'awaiting_platform_html':
        return <PlatformChamber />;

      case 'awaiting_scribe':
        return <ScribesChamber />;

      case 'awaiting_platform_text':
        return <TextPlatformChamber />;

      case 'asset_revealed':
        return <FinalScroll />;
        
      case 'scroll_unfurled':
        if (!unfurledContent) return <div className="text-center p-8">Error: The scroll content was lost.</div>;
        return (
            <ScrollUnfurled 
                title={unfurledContent.title}
                content={unfurledContent.content}
                onBack={returnToScroll}
            />
        );

      case 'prompt_unveiled':
        if (!unveiledPrompt) return <div className="text-center p-8">Error: The prompt was lost in the ether.</div>;
        const platformDetails = unveiledPrompt.type === 'Image' 
          ? { name: 'Midjourney', url: 'https://www.midjourney.com/', instructions: 'Copy the prompt below and paste it into the Midjourney Discord bot.' }
          : { name: 'RunwayML', url: 'https://runwayml.com/', instructions: 'Copy the prompt below and use it in a text-to-video generator.' };
        return (
          <PromptUnveiled
            promptType={unveiledPrompt.type}
            promptTitle={unveiledPrompt.title}
            promptContent={unveiledPrompt.content}
            platformName={platformDetails.name}
            platformUrl={platformDetails.url}
            instructions={platformDetails.instructions}
            onBack={returnToScroll}
          />
        );

      case 'forging_angles':
      case 'forging_asset':
      case 'unfurling_scroll':
      case 'forging_prompt':
        // CORRECTED: Pass the required props to RitualScreen
        return (
          <RitualScreen
            key={`forge-ritual-${status}`}
            ritualPromise={ritualPromise}
            onRitualComplete={handleRitualComplete}
          />
        );
      
      default:
        return <div className="text-center p-8">Preparing the Forge...</div>;
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
// --- END OF FILE frontend/src/components/ForgeManager.tsx ---