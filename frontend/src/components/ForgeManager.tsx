// --- START OF FILE src/components/ForgeManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useMarketingStore } from '@/store/marketingStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import AnvilForm from './AnvilForm';
import HallOfAngles from './HallOfAngles';
import ScribesChamber from './ScribesChamber';
import PlatformChamber from './PlatformChamber';
import FinalScroll from './FinalScroll';
import PromptUnveiled from './PromptUnveiled';
import ScrollUnfurled from './ScrollUnfurled'; // Summoning the final component.

/**
 * ForgeManager: The master controller for the entire Skald's Forge workflow.
 * It reads the status from the marketingStore and renders the appropriate UI.
 */
export default function ForgeManager() {
  const { 
    status, 
    invokeForge, 
    chosenAssetType, 
    commandScribe, 
    unveiledPrompt,
    unfurledContent,
    returnToScroll 
  } = useMarketingStore();

  useEffect(() => {
    if (status === 'idle') {
      invokeForge();
    }
  }, [status, invokeForge]);

  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_anvil':
        return <AnvilForm />;
      
      case 'angles_revealed':
        return <HallOfAngles />;

      case 'awaiting_platform':
        return <PlatformChamber />;

      case 'awaiting_scribe':
        if (!chosenAssetType) return <div className="text-center p-8">Error: Asset Type not chosen.</div>;
        return (
          <ScribesChamber 
            assetType={chosenAssetType} 
            onLengthSelect={(length) => commandScribe(length)} 
          />
        );

      case 'asset_revealed':
        return <FinalScroll />;
        
      // NEW LOGIC: When the status is 'scroll_unfurled', show the ScrollUnfurled component.
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
          ? { name: 'Midjourney', url: 'https://www.midjourney.com/', instructions: 'Copy the prompt below and paste it into the Midjourney Discord bot to generate your image.' }
          : { name: 'RunwayML', url: 'https://runwayml.com/', instructions: 'Copy the prompt below and use it in a text-to-video generator like RunwayML or Sora to create your video.' };
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

      // The ritual screen is shown for all "forging" and "unfurling" states.
      case 'forging_angles':
      case 'forging_asset':
      case 'unfurling_scroll':
      case 'forging_prompt':
        return <RitualScreen />;
      
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
// --- END OF FILE src/components/ForgeManager.tsx ---