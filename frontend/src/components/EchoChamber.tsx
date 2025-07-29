'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useContentStore } from '@/store/contentStore';
import { useSession } from '@/hooks/useSession';
import InputRune from './InputRune';
import SagaButton from './SagaButton';

/**
 * EchoChamber: The component where a user provides the post they wish to comment on,
 * in the context of their chosen Content Spark.
 */
export default function EchoChamber() {
  const { chosenSpark, submitPostToCommentOn, status } = useContentStore();
  const isLoading = status === 'weaving_comment';

  const { sessionId, isLoading: isSessionLoading } = useSession();

  const [postContent, setPostContent] = useState('');

  const handleSubmit = () => {
    if (!postContent) {
      alert("The Weaver requires the original post's text to craft a worthy echo.");
      return;
    }
    if (isSessionLoading || !sessionId) {
      alert("Session is not yet ready. Please wait a moment.");
      return;
    }
    submitPostToCommentOn(postContent, sessionId);
  };

  return (
    <motion.div
      key="echo-chamber"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header className="text-center mb-12">
        <h2 className="font-serif text-4xl md:text-5xl font-bold text-white">
          The Echo Chamber
        </h2>
        <p className="mt-4 text-lg text-saga-text-dark max-w-2xl mx-auto">
          Provide the words of another, and Saga shall weave an echo of wisdom that enhances the conversation.
        </p>
      </header>

      <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} 
          className="space-y-8"
        >
          <div className="bg-saga-bg p-4 rounded-lg border border-saga-primary/20">
            <p className="text-sm font-serif text-saga-primary mb-2">Your Strategic Angle:</p>
            <h3 className="font-semibold text-lg text-saga-text-light">{chosenSpark?.title}</h3>
            <p className="text-sm text-saga-text-dark mt-1">{chosenSpark?.description}</p>
          </div>

          <InputRune
            id="postContent"
            label="Post to Comment On"
            as="textarea"
            placeholder="Paste the text of the social media post you wish to respond to here..."
            value={postContent}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPostContent(e.target.value)}
          />

          <div className="pt-4 text-center">
            <SagaButton 
              onClick={handleSubmit} 
              className="py-3 px-8 text-lg"
              disabled={isLoading || isSessionLoading}
            >
              {isSessionLoading ? "Awaiting Session..." : (isLoading ? "Observing Ritual..." : "Weave Insightful Comments")}
            </SagaButton>
          </div>
        </form>
      </div>
    </motion.div>
  );
}