// --- START OF FILE src/components/ScriptoriumForm.tsx ---
'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GrimoirePage, createScroll, updateScroll, generateTitles, generateContent, TitleConcept } from '@/services/grimoireApi';
import InputRune from './InputRune';
import SagaButton from './SagaButton';

// SAGA LOGIC: Define the properties for our new, powerful form.
interface ScriptoriumFormProps {
  scroll?: GrimoirePage | null; // The existing scroll to edit (if any).
  onClose: () => void; // A function to return to the manage view.
}

/**
 * ScriptoriumForm: The final, multi-modal form for creating, editing,
 * and divining new scrolls with AI assistance.
 */
export default function ScriptoriumForm({ scroll, onClose }: ScriptoriumFormProps) {
  // --- STATE MANAGEMENT ---
  const [mode, setMode] = useState<'manual' | 'ai_topic' | 'ai_titles' | 'ai_content'>('manual');
  
  // Form fields
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [summary, setSummary] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState('');

  // AI workflow state
  const [topic, setTopic] = useState('');
  const [titleConcepts, setTitleConcepts] = useState<TitleConcept[]>([]);
  
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  // SAGA LOGIC: Pre-fill the form if we are in "Edit Mode".
  useEffect(() => {
    if (scroll) {
      setTitle(scroll.title);
      setSlug(scroll.slug);
      setSummary(scroll.summary);
      setContent(scroll.content);
      setTags(scroll.tags.join(', '));
      setMode('manual'); // Start in manual mode when editing
    }
  }, [scroll]);

  const adminKey = typeof window !== 'undefined' ? localStorage.getItem('saga-admin-key') : null;

  // --- AI RITUALS ---
  const handleGenerateTitles = async () => {
    if (!topic || !adminKey) return;
    setIsLoading(true);
    setMessage('Saga is divining title concepts...');
    const concepts = await generateTitles(topic, adminKey);
    setTitleConcepts(concepts);
    setMode('ai_titles');
    setIsLoading(false);
    setMessage('');
  };

  const handleSelectTitle = async (concept: TitleConcept) => {
    setIsLoading(true);
    setMessage('Saga is inscribing the full scroll...');
    const generated = await generateContent(concept.title, topic, adminKey);
    if (generated && adminKey) {
      setTitle(concept.title);
      setSlug(concept.slug);
      setSummary(generated.summary);
setContent(generated.content);
      setMode('manual'); // Switch to manual mode for final edits
    } else {
      setMessage('Error: Saga could not generate the content.');
    }
    setIsLoading(false);
  };

  // --- SAVE / UPDATE RITE ---
  const handleSubmit = async () => {
    if (!title || !summary || !content || !adminKey) {
      setMessage("Title, Summary, and Content are required. The sacred key must also be present.");
      return;
    }
    setIsLoading(true);

    const pageData = {
      title, slug, summary, content,
      tags: tags.split(',').map(tag => tag.trim()).filter(Boolean),
    };

    const result = scroll
      ? await updateScroll(scroll.id, pageData, adminKey) // UPDATE existing
      : await createScroll(pageData, adminKey);           // CREATE new

    setMessage(result.message);
    setIsLoading(false);
    if (result.success) {
      setTimeout(() => onClose(), 1500); // Go back to the manager on success
    }
  };

  // --- RENDER LOGIC ---
  const renderAiTopicView = () => (
    <div className="space-y-6">
        <InputRune id="topic" label="Scroll Topic" placeholder="What subject shall Saga divine?" value={topic} onChange={(e) => setTopic(e.target.value)} />
        <SagaButton onClick={handleGenerateTitles} className="w-full">{isLoading ? 'Divining...' : 'Generate Title Concepts'}</SagaButton>
    </div>
  );

  const renderAiTitlesView = () => (
    <div>
        <h3 className="font-serif text-2xl text-saga-primary mb-4 text-center">Choose a Title</h3>
        <div className="space-y-4">
            {titleConcepts.map(concept => (
                <button key={concept.slug} onClick={() => handleSelectTitle(concept)} className="w-full text-left p-4 bg-saga-bg rounded-md hover:border-saga-primary border border-transparent transition-colors">
                    <p className="font-bold text-saga-text-light">{concept.title}</p>
                    <p className="text-sm text-saga-text-dark font-mono">{concept.slug}</p>
                </button>
            ))}
        </div>
    </div>
  );

  const renderManualView = () => (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="space-y-8">
      <InputRune id="title" label="Scroll Title" value={title} onChange={(e) => setTitle(e.target.value)} />
      <InputRune id="slug" label="Slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
      <InputRune id="summary" label="Summary" as="textarea" value={summary} onChange={(e) => setSummary(e.target.value)} />
      <InputRune id="content" label="Content (HTML)" as="textarea" value={content} onChange={(e) => setContent(e.target.value)} className="min-h-[300px] font-mono" />
      <InputRune id="tags" label="Tags (comma-separated)" value={tags} onChange={(e) => setTags(e.target.value)} optional />
      <div className="pt-4 text-center">
        <SagaButton onClick={handleSubmit} className="w-full">{isLoading ? 'Inscribing...' : (scroll ? 'Update Scroll' : 'Inscribe Scroll')}</SagaButton>
      </div>
    </form>
  );

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg">
      {/* Mode Toggle Buttons */}
      {!scroll && ( // Only show mode toggle when creating a new post
        <div className="flex justify-center border-b border-white/20 pb-6 mb-8 gap-4">
            <button onClick={() => setMode('manual')} className={`font-serif pb-2 ${mode === 'manual' ? 'text-saga-primary border-b-2 border-saga-primary' : 'text-saga-text-dark'}`}>Manual Inscription</button>
            <button onClick={() => setMode('ai_topic')} className={`font-serif pb-2 ${mode.startsWith('ai_') ? 'text-saga-primary border-b-2 border-saga-primary' : 'text-saga-text-dark'}`}>Divine a Scroll</button>
        </div>
      )}
      
      <AnimatePresence mode="wait">
        <motion.div key={mode} initial={{opacity: 0}} animate={{opacity: 1}} exit={{opacity: 0}}>
            {mode === 'manual' && renderManualView()}
            {mode === 'ai_topic' && renderAiTopicView()}
            {mode === 'ai_titles' && renderAiTitlesView()}
        </motion.div>
      </AnimatePresence>

      {message && <p className={`text-center mt-6 ${message.startsWith('Error:') ? 'text-red-400' : 'text-green-400'}`}>{message}</p>}

      <div className="text-center mt-8">
        <button onClick={onClose} className="font-serif text-saga-text-dark hover:text-saga-primary transition-colors">← Return to Manager</button>
      </div>
    </motion.div>
  );
}
// --- END OF FILE src/components/ScriptoriumForm.tsx ---