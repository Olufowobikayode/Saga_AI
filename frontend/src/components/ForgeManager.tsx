// --- START OF FILE src/components/ForgeManager.tsx ---
'use client';

import React, { useEffect } from 'react';
import { useMarketingStore } from '@/store/marketingStore';
import { AnimatePresence } from 'framer-motion';
import RitualScreen from './RitualScreen';
import AnvilForm from './AnvilForm';
import HallOfAngles from './HallOfAngles';
import ScribesChamber from './ScribesChamber';
import FinalScroll from './FinalScroll';
import PromptUnveiled from './PromptUnveiled'; // Summoning the final component.

/**
 * ForgeManager: The master controller for the entire Skald's Forge workflow.
 * It reads the status from the marketingStore and renders the appropriate UI.
 */
export default function ForgeManager() {
  // SAGA LOGIC: Connect to the Mind of the Skald to get all necessary state and functions.
  const { 
    status, 
    invokeForge, 
    chosenAssetType, 
    commandScribe, 
    unveiledPrompt, 
    returnToScroll 
  } = useMarketingStore();

  useEffect(() => {
    if (status === 'idle') {
      invokeForge();
    }
  }, [status, invokeForge]);

  // This function now handles every possible state in our complex workflow.
  const renderCurrentStage = () => {
    switch (status) {
      case 'awaiting_anvil':
        return <AnvilForm />;
      
      case 'angles_revealed':
        return <HallOfAngles />;

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

      // NEW LOGIC: When the status is 'prompt_unveiled', we show the PromptUnveiled component.
      case 'prompt_unveiled':
        if (!unveiledPrompt) return <div className="text-center p-8">Error: The prompt was lost in the ether.</div>;
        
        // We define the platform details here based on the prompt type.
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
            onBack={returnToScroll} // The back button calls the rite to return to the previous state.
          />
        );

      // The ritual screen is shown for all "forging" states.
      case 'forging_angles':
      case 'forging_asset':
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
      </An-imatePresence>
    </div>
  );
}
// --- END OF FILE src/components/ForgeManager.tsx ---