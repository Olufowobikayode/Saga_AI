// --- START OF FILE src/components/FinalContentScroll.tsx ---
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { useContentStore } from '@/store/contentStore';

// SAGA UI: A reusable card for displaying a piece of generated content.
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
  const isLoading = status === 'weaving_social_post' || status === 'weaving_comment' || status === 'weaving_blog';

  const handleCopy = () => navigator.clipboard.writeText(content);

  const handleShare = () => {
    // Basic share functionality. More advanced logic can be added.
    const text = encodeURIComponent(content);
    let url = '';
    if (platform.toLowerCase().includes('twitter')) {
      url = `https://twitter.com/intent/tweet?text=${text}`;
    } else if (platform.toLowerCase().includes('facebook')) {
      url = `https://www.facebook.com/sharer/sharer.php?u=example.com"e=${text}`; // Needs a URL to share
    } else if (platform.toLowerCase().includes('linkedin')) {
      url = `https://www.linkedin.com/shareArticle?mini=true&url=example.com&title=MySaga&summary=${text}`; // Needs a URL
    }
    if (url) window.open(url, '_blank');
  };

  return (
    <div className="bg-saga-surface p-6 rounded-lg border border-white/10">
      <p className="text-saga-text-light whitespace-pre-wrap font-sans text-lg">{content}</p>
      <div className="flex items-center space-x-4 mt-6 pt-4 border-t border-white/10">
        <button onClick={handleCopy} className="text-sm text-saga-primary hover:text-saga-secondary">Copy</button>
        {showShare && <button onClick={handleShare} className="text-sm text-saga-primary hover:text-saga-secondary">Share</button>}
        <button onClick={regenerate} className="text-sm text-saga-primary hover:text-saga-secondary flex items-center">
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
  const { finalContent, status, chosenRealm, resetLoom } = useContentStore();

  if (!finalContent) {
    return <div className="text-center p-8">The prophecy is faint... No content was found.</div>;
  }

  // SAGA LOGIC: This function determines which layout to render based on the final status.
  const renderContent = () => {
    switch (status) {
      case 'social_post_woven':
        return (
          <ContentCard 
            content={finalContent.post_text} 
            showShare={true} 
            platform={chosenRealm || ''} 
          />
          // In the future, we could add the clickable Image/Video prompt cards here.
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
          <div>
            <h2 className="font-serif text-3xl text-saga-secondary mb-4">{finalContent.title}</h2>
            <div 
              className="prose prose-lg prose-invert max-w-none prose-headings:font-serif prose-p:text-saga-text-light"
              dangerouslySetInnerHTML={{ __html: finalContent.body }} 
            />
            <div className="flex items-center space-x-4 mt-6 pt-4 border-t border-white/10">
               <button onClick={() => navigator.clipboard.writeText(finalContent.body)} className="text-sm text-saga-primary hover:text-saga-secondary">Copy HTML</button>
               <button onClick={resetLoom} className="text-sm text-saga-primary hover:text-saga-secondary flex items-center">Regenerate <span className="ml-1">✨</span></button>
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
// --- END OF FILE src/components/FinalContentScroll.tsx ---