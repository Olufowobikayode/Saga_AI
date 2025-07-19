import React, { useState } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import { Lightbulb, FileText, ShoppingCart, BarChart2, Brain, Loader2, Send, Bot, PenSquare } from 'lucide-react';

import './App.css'; // Your custom styles

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// --- Main App Layout ---
function App() {
  const [activeStack, setActiveStack] = useState('idea');

  const stacks = [
    { id: 'idea', label: 'Idea Stack', icon: Lightbulb },
    { id: 'content', label: 'Content Stack', icon: FileText },
    { id: 'commerce', label: 'Commerce Stack', icon: ShoppingCart },
    { id: 'strategy', label: 'Strategy Stack', icon: BarChart2 },
    { id: 'marketing', label: 'Marketing Stack', icon: Send },
    { id: 'blog', label: 'Blog Stack', icon: PenSquare },
  ];

  const renderActiveStack = () => {
    switch (activeStack) {
      case 'idea': return <IdeaStack />;
      case 'content': return <ContentStack />;
      // ... (add other stacks here when you build them)
      default: return <div className="p-8 text-center text-gray-500">{activeStack.replace(/^\w/, c => c.toUpperCase())} Stack is coming soon!</div>;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Toaster position="top-center" reverseOrder={false} />
      <header className="bg-white shadow-md p-4 flex items-center justify-between z-10">
        <div className="flex items-center gap-4">
          <Brain size={32} className="text-indigo-600" />
          <h1 className="text-2xl font-bold text-gray-800">NicheStack AI</h1>
        </div>
      </header>
      <div className="flex flex-1">
        <aside className="w-64 bg-white shadow-lg p-4">
          <nav className="flex flex-col gap-2">
            {stacks.map(stack => (
              <button key={stack.id} onClick={() => setActiveStack(stack.id)}
                className={`flex items-center gap-3 p-3 rounded-md text-left font-semibold transition-colors ${activeStack === stack.id ? 'bg-indigo-100 text-indigo-700' : 'text-gray-600 hover:bg-gray-100'}`}>
                <stack.icon size={20} />{stack.label}
              </button>
            ))}
          </nav>
        </aside>
        <main className="flex-1 p-8 overflow-y-auto">{renderActiveStack()}</main>
      </div>
    </div>
  );
}

// --- STACK 1: The Idea Stack Component ---
const IdeaStack = () => {
    // ... (This component remains the same as the previous version)
};

// --- STACK 2: The Content Stack Component (with interactive placeholders) ---
const ContentStack = () => {
    const [basePost, setBasePost] = useState(null);
    const [loading, setLoading] = useState(false);
    const [selectedPlatform, setSelectedPlatform] = useState(null);

    const handleGenerateBase = async () => {
        setLoading(true);
        setSelectedPlatform(null);
        toast.loading('Generating base content idea...');
        try {
            const response = await axios.get(`${API_URL}/api/content-stack/generate-base-post`);
            setBasePost(response.data);
            toast.dismiss();
            toast.success('Base content generated!');
        } catch(error) {
            toast.dismiss();
            toast.error('Failed to generate base content.');
        } finally {
            setLoading(false);
        }
    };

    if (selectedPlatform) {
        return <ContentCustomizer platform={selectedPlatform} onBack={() => setSelectedPlatform(null)} />;
    }

    return (
        <div>
            <h2 className="text-3xl font-bold text-gray-800">The Content Stack</h2>
            <p className="mt-2 text-gray-600">Generate a cohesive, multi-platform content package from a single idea.</p>
            <button onClick={handleGenerateBase} disabled={loading} className="mt-6 flex items-center justify-center gap-2 p-3 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 disabled:bg-gray-400">
                {loading ? <Loader2 className="animate-spin"/> : <Wand2 />} Generate Base Post Idea
            </button>
            
            {basePost && (
                <div className="mt-8 bg-white p-6 rounded-lg shadow-lg">
                    <h3 className="text-xl font-bold text-gray-800">Your Generated Idea:</h3>
                    <p className="mt-2 text-lg text-indigo-700 font-semibold">"{basePost.catchy_post}"</p>
                    <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                        {['Facebook', 'X (Twitter)', 'LinkedIn', 'Instagram'].map(platform => (
                            <div key={platform} onClick={() => setSelectedPlatform(platform)}
                                className="p-4 border rounded-lg text-center cursor-pointer hover:border-indigo-500 hover:shadow-md transition-all">
                                <p className="font-semibold">{platform}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

const ContentCustomizer = ({ platform, onBack }) => {
    const tones = ['Fun', 'Educational', 'Inspirational', 'Professional'];
    const lengths = ['Short', 'Medium', 'Long'];

    return (
        <div>
            <button onClick={onBack} className="text-indigo-600 font-semibold mb-4">← Back to Idea</button>
            <h2 className="text-3xl font-bold text-gray-800">Customize for {platform}</h2>
            <div className="mt-6 bg-white p-6 rounded-lg shadow-lg space-y-4">
                <div>
                    <label className="block font-semibold mb-2">Tone</label>
                    <select className="w-full p-2 border rounded-md"><options value="">Select Tone</options>{tones.map(t => <option key={t}>{t}</option>)}</select>
                </div>
                <div>
                    <label className="block font-semibold mb-2">Length</label>
                    <select className="w-full p-2 border rounded-md"><options value="">Select Length</options>{lengths.map(l => <option key={l}>{l}</option>)}</select>
                </div>
                <div className="pt-4 border-t">
                    <h3 className="font-semibold">Generated Post (Placeholder):</h3>
                    <div className="mt-2 p-4 bg-gray-50 rounded-md border">
                        This is a placeholder for a {platform} post with a [selected tone] tone and [selected length]. The real AI would generate the full text here based on your selections.
                    </div>
                </div>
                <button className="mt-4 p-3 w-full bg-green-600 text-white font-semibold rounded-md hover:bg-green-700">Share to {platform}</button>
            </div>
        </div>
    );
};

export default App;