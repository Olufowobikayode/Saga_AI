// --- START OF REFACTORED FILE src/components/FinalContentScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useContentStore } from '@/store/contentStore';
import { useSession } from '@/hooks/useSession'; // <-- 1. IMPORT HOOK

// A reusable card for displaying a piece of generated content.
const ContentCard = ({ 
  content, 
  showShare = false, 
  platform = '' 
}: { 
  content: string; 
  showShare?: boolean; 
  platform?: string; 
}) => {
  const { regenerate, status } = useContentStore();
  const isLoading = ['weaving_social_post', 'weaving_comment'].includes(status);

  // --- 2. USE SESSION HOOK ---
  const { sessionId, isLoading: isSessionLoading } = useSession();

  const handleCopy = () => navigator.clipboard.writeText(content);
  
  const handleRegenerate = () => {
    if (isSessionLoading || !sessionId) {
      alert("Session is not yet ready. Please wait a moment.");
      return;
    }
    // --- 3. PASS SESSION ID TO STORE ACTION ---
    regenerate(sessionId);
  };

  const handleShare = () => {
    const text = encodeURIComponent(content);
    let url = '';
    if (platform.toLowerCase().includes('twitter')) url = `https://twitter.com/intent/tweet?text=${text}`;
    else if (platform.toLowerCase().includes('facebook')) url = `https://www.facebook.com/sharer/sharer.php?u=example.com"e=${text}`;
    else if (platform.toLowerCase().includes('linkedin')) url = `https://www.linkedin.com/shareArticle?mini=true&url=example.com&title=Saga%20Prophecy&summary=${text}`;
    if (url) window.open(url, '_blank');
  };

  return (
    <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
      <p className="text-saga-text-light whitespace-pre-wrap font-sans text-lg">{content}</p>
      <div className="flex items-center space-x-4 mt-6 pt-4 border-t border-white/10">
        <button onClick={handleCopy} className="text-sm font-semibold text-saga-primary hover:text-saga-secondary">Copy</button>
        {showShare && <button onClick={handleShare} className="text-sm font-semibold text-saga-primary hover:text-saga-secondary">Share</button>}
        <button 
            onClick={handleRegenerate} 
            disabled={isLoading || isSessionLoading}
            className="text-sm font-semibold text-saga-primary hover:text-saga-secondary flex items-center disabled:opacity-50"
        >
          {isLoading ? 'Regenerating...' : 'Regenerate'}
          {!isLoading && <span className="ml-1">✨</span>}
        </button>
      </div>
    </div>
  );
};

/**
 * FinalContentScroll: Displays the final generated content from any of the Weaver's paths.
 */
export default function FinalContentScroll() {
  const { finalContent, status, chosenRealm, resetLoom, regenerate } = useContentStore();
  
  // Need the session hook here as well for the blog post's regenerate button
  const { sessionId, isLoading: isSessionLoading } = useSession();
  const isBlogLoading = status === 'weaving_blog';

  const handleBlogRegenerate = () => {
    if (isSessionLoading || !sessionId) {
      alert("Session is not yet ready. Please wait a moment.");
      return;
    }
    regenerate(sessionId);
  };

  if (!finalContent) {
    return <div className="text-center p-8">The prophecy is faint... No content was found.</div>;
  }

  const renderContent = () => {
    switch (status) {
      case 'social_post_woven':
        return (
          <ContentCard 
            content={finalContent.post_text} 
            showShare={true} 
            platform={chosenRealm || ''} 
          />
        );

      case 'comment_woven':
        return (
          <div className="space-y-6">
            <h3 className="font-serif text-2xl text-saga-primary text-center">Generated Comment Options</h3>
            {finalContent.comments.map((comment: string, index: number) => (
              <ContentCard key={index} content={comment} />
            ))}
          </div>
        );

      case 'blog_woven':
        return (
          <div className="bg-saga-surface p-6 md:p-8 rounded-lg border border-white/10">
            <h2 className="font-serif text-3xl text-saga-secondary mb-4">{finalContent.title}</h2>
            <div 
              className="prose prose-lg prose-invert max-w-none prose-headings:font-serif prose-p:text-saga-text-light"
              dangerouslySetInnerHTML={{ __html: finalContent.body }} 
            />
            <div className="flex items-center space-x-4 mt-6 pt-4 border-t border-white/10">
               <button onClick={() => navigator.clipboard.writeText(finalContent.body)} className="text-sm font-semibold text-saga-primary hover:text-saga-secondary">Copy HTML</button>
               <button 
                  onClick={handleBlogRegenerate} 
                  disabled={isBlogLoading || isSessionLoading}
                  className="text-sm font-semibold text-saga-primary hover:text-saga-secondary flex items-center disabled:opacity-50"
                >
                  {isBlogLoading ? 'Regenerating...' : 'Regenerate'}
                  {!isBlogLoading && <span className="ml-1">✨</span>}
                </button>
            </div>
          </div>
        );
        
      default:
        return <p>An unknown thread was woven.</p>;
    }
  };

  return (
    <motion.div
      key="final-content-scroll"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Saga is Woven
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark">
          Your prophecy is complete. Use this wisdom as you see fit.
        </p>
      </header>

      <div>
        {renderContent()}
      </div>

      <div className="text-center mt-16">
        <button onClick={resetLoom} className="font-serif text-lg text-saga-text-dark hover:text-saga-primary transition-colors">
          ← Weave Another Saga
        </button>
      </div>
    </motion.div>
  );
}
// --- END OF REFACTORED FILE src/components/FinalContentScroll.tsx ---