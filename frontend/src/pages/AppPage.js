// file: frontend/src/pages/AppPage.js

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import { Link } from 'react-router-dom';
import { Home, Lightbulb, FileText, ShoppingCart, BarChart2, Brain, Send, PenSquare, Loader2, Copy } from 'lucide-react';
import '../App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost.com:8001';

// --- Reusable Components ---

const Header = () => (
  <header className="bg-white shadow-md p-4 flex items-center justify-between z-10">
    <div className="flex items-center gap-4">
      <Brain size={32} className="text-indigo-600" />
      <h1 className="text-2xl font-bold text-gray-800">NicheStack AI</h1>
    </div>
    <Link to="/" className="flex items-center gap-2 text-gray-600 hover:text-indigo-600 font-semibold transition-colors">
      <Home size={18} />
      <span>Homepage</span>
    </Link>
  </header>
);

const StackButton = ({ stack, activeStack, setActiveStack }) => (
    <button
      onClick={() => setActiveStack(stack.id)}
      className={`w-full flex items-center gap-3 p-3 rounded-md text-left font-semibold transition-colors ${
        activeStack === stack.id 
          ? 'bg-indigo-100 text-indigo-700'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
      }`}
    >
      <stack.icon size={20} />
      {stack.label}
    </button>
);

const LoadingSpinner = ({ text }) => (
    <div className="text-center py-12">
        <Loader2 className="h-10 w-10 text-indigo-600 animate-spin mx-auto" />
        <p className="mt-4 font-semibold text-gray-700">{text}</p>
    </div>
);

// --- The Main App Page Component ---
function AppPage() {
  const [activeStack, setActiveStack] = useState('idea');
  const [interest, setInterest] = useState('AI tools for content creators');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const stacks = [
    { id: 'idea', label: 'Idea Stack', icon: Lightbulb, inputLabel: "Enter a Broad Interest", buttonText: "Discover Business Ideas" },
    { id: 'content', label: 'Content Stack', icon: FileText, inputLabel: "Enter a Niche/Topic", buttonText: "Generate Content Package" },
    { id: 'commerce', label: 'Commerce Stack', icon: ShoppingCart, inputLabel: "Enter a Product Category", buttonText: "Analyze E-commerce Sites" },
    { id: 'strategy', label: 'Strategy Stack', icon: BarChart2, inputLabel: "Enter Your Niche", buttonText: "Find SEO Opportunities" },
    { id: 'marketing', label: 'Marketing Stack', icon: Send, inputLabel: "Enter a Product Name", buttonText: "Generate Marketing Funnel" },
    { id: 'blog', label: 'Blog Stack', icon: PenSquare, inputLabel: "Enter a Blog Post Topic", buttonText: "Generate SEO Article" },
  ];

  const currentStack = stacks.find(s => s.id === activeStack);

  const handleSubmit = async () => {
    if (!interest.trim()) {
        toast.error("Please enter an interest or topic.");
        return;
    }
    setLoading(true);
    setResults(null);
    
    // In a real app, this is where you would trigger the rewarded ad
    toast.loading('Oracle AI at work... (Ad would show now)');

    try {
        const response = await axios.post(`${API_URL}/api/${activeStack}-stack`, { interest });
        setResults(response.data.data);
        toast.dismiss();
        toast.success(`Analysis complete for ${activeStack} Stack!`);
    } catch (error) {
        toast.dismiss();
        const errorMsg = error.response?.data?.detail || `Failed to run ${activeStack} Stack.`;
        toast.error(errorMsg);
        console.error(`Error running ${activeStack} stack:`, error);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <div className="flex flex-1">
        <aside className="w-80 bg-white shadow-lg p-6 flex-col flex">
            <h2 className="text-lg font-bold text-gray-800 mb-4">Control Panel</h2>
            <div className="space-y-2 mb-6">
                {stacks.map(stack => (
                    <StackButton key={stack.id} stack={stack} activeStack={activeStack} setActiveStack={setActiveStack} />
                ))}
            </div>
            
            <div className="mt-auto bg-gray-50 p-4 rounded-lg border">
                <label htmlFor="interest-input" className="block font-semibold mb-2 text-gray-700">{currentStack.inputLabel}</label>
                <textarea id="interest-input" rows="3"
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
                    value={interest} onChange={(e) => setInterest(e.target.value)}
                />
                <button onClick={handleSubmit} disabled={loading} className="w-full mt-3 flex items-center justify-center gap-2 p-3 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 disabled:bg-gray-400">
                    {loading ? <Loader2 className="animate-spin" /> : <currentStack.icon size={18} />}
                    {currentStack.buttonText}
                </button>
            </div>
        </aside>

        <main className="flex-1 p-8 overflow-y-auto">
            <div className="bg-white p-8 rounded-lg shadow-lg min-h-full">
                {loading ? (
                    <LoadingSpinner text={`Running ${currentStack.label}...`} />
                ) : results ? (
                    <div className="results-output">
                        <pre>{JSON.stringify(results, null, 2)}</pre>
                    </div>
                ) : (
                    <div className="text-center text-gray-500 pt-20">
                        <Brain size={48} className="mx-auto mb-4" />
                        <h2 className="text-2xl font-bold">Welcome to the {currentStack.label}</h2>
                        <p className="mt-2 max-w-md mx-auto">Enter your topic in the Control Panel on the left and click "{currentStack.buttonText}" to get started.</p>
                    </div>
                )}
            </div>
        </main>
      </div>
    </div>
  );
}

export default AppPage;```