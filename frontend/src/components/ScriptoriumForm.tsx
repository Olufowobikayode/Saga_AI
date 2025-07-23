// --- START OF FILE src/components/ScriptoriumForm.tsx ---
'use client';

import React, { useState } from 'react';
import { createScroll } from '@/services/grimoireApi';
import InputRune from './InputRune';
import SagaButton from './SagaButton';

/**
 * ScriptoriumForm: The actual content creation form for the admin.
 */
export default function ScriptoriumForm() {
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState(''); // Comma-separated tags
  
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async () => {
    setMessage('');
    if (!title || !summary || !content) {
      setMessage("A scroll must have a Title, Summary, and Content.");
      return;
    }

    const adminKey = localStorage.getItem('saga-admin-key');
    if (!adminKey) {
      setMessage("Authentication error. The sacred key is missing.");
      return;
    }

    setIsLoading(true);

    const pageData = {
      title,
      summary,
      content,
      tags: tags.split(',').map(tag => tag.trim()).filter(Boolean), // Process tags
    };

    const result = await createScroll(pageData, adminKey);

    if (result.success) {
      setMessage(result.message);
      // Clear the form on success
      setTitle('');
      setSummary('');
      setContent('');
      setTags('');
    } else {
      setMessage(`Error: ${result.message}`);
    }
    
    setIsLoading(false);
  };

  return (
    <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
      <form 
        onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} 
        className="space-y-8"
      >
        <InputRune
          id="title"
          label="Scroll Title"
          placeholder="The title of your wisdom..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        
        <InputRune
          id="summary"
          label="Summary"
          as="textarea"
          placeholder="A brief summary for the Grimoire library page..."
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
        />

        <InputRune
          id="content"
          label="Content (HTML)"
          as="textarea"
          placeholder="Inscribe the full wisdom of the scroll here. You can use HTML tags like <h2>, <p>, <ul>, <li>, <strong>..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="min-h-[300px] font-mono" // Larger text area for content
        />

        <InputRune
          id="tags"
          label="Tags"
          placeholder="e.g., marketing, seo, strategy"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          optional
        />

        <div className="pt-4 text-center">
          <SagaButton onClick={handleSubmit} className="w-full">
            {isLoading ? "Inscribing..." : "Inscribe Scroll into Grimoire"}
          </SagaButton>
        </div>

        {message && (
          <p className={`text-center mt-4 ${message.startsWith('Error:') ? 'text-red-400' : 'text-saga-primary'}`}>
            {message}
          </p>
        )}
      </form>
    </div>
  );
}
// --- END OF FILE src/components/ScriptoriumForm.tsx ---