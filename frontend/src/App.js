import React, { useState } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import { Target, Search, Wand2 } from 'lucide-react';
import './App.css'; // Import the custom override styles

// Setup the base URL for the API from environment variables
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// --- Reusable Components with Tailwind CSS ---

const Header = () => (
  <header className="bg-white shadow-md p-4 flex items-center gap-4">
    <Target size={32} className="text-blue-600" />
    <h1 className="text-2xl font-bold text-gray-800">Oracle Engine</h1>
  </header>
);

const NicheSelector = ({ niche, setNiche, contentType, setContentType, handleAnalyze, handleGenerate, loading, analysisResults }) => {
  const niches = ["Fitness", "Crypto", "SaaS", "Marketing", "E-commerce", "Health", "AI", "Real Estate"];
  const contentTypes = ["Social Post", "Ad Copy", "Affiliate Review", "Print on Demand", "E-commerce Product"];

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex flex-col gap-4">
        <div>
          <label htmlFor="niche-select" className="block font-semibold mb-2 text-gray-700">
            1. Choose Your Niche
          </label>
          <select id="niche-select" className="w-full p-3 border border-gray-300 rounded-md bg-white focus:ring-2 focus:ring-blue-500" value={niche} onChange={(e) => setNiche(e.target.value)}>
            {niches.map(n => <option key={n} value={n.toLowerCase()}>{n}</option>)}
          </select>
        </div>
        
        <button
          className="w-full flex items-center justify-center gap-2 p-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          onClick={handleAnalyze} disabled={!niche || loading.isAnalyzing}
        >
          <Search size={18} />
          {loading.isAnalyzing ? 'Analyzing Niche...' : 'Analyze Niche'}
        </button>

        {analysisResults && (
          <>
            <div className="border-t border-gray-200 my-2"></div>
            <div>
              <label htmlFor="content-type-select" className="block font-semibold mb-2 text-gray-700">
                2. Select Content Type
              </label>
              <select id="content-type-select" className="w-full p-3 border border-gray-300 rounded-md bg-white focus:ring-2 focus:ring-blue-500" value={contentType} onChange={(e) => setContentType(e.target.value)}>
                {contentTypes.map(type => <option key={type} value={type.toLowerCase().replace(/ /g, '_')}>{type}</option>)}
              </select>
            </div>
            <button
              className="w-full flex items-center justify-center gap-2 p-3 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
              onClick={handleGenerate} disabled={!contentType || loading.isGenerating}
            >
              <Wand2 size={18} />
              {loading.isGenerating ? 'Generating Content...' : 'Generate Content'}
            </button>
          </>
        )}
      </div>
    </div>
  );
};

const ResultsDisplay = ({ analysisResults, generatedContent }) => {
  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text);
    toast.success(`${type} copied to clipboard!`);
  };

  const ContentViewer = ({ content }) => {
    if (!content) return null;
    const sections = content.split('---').filter(section => section.trim() !== '');

    return sections.map((section, index) => {
      const trimmedSection = section.trim();
      
      // Look for a title in the format of `**Title:**`
      const titleMatch = trimmedSection.match(/^\*\*(.*?):\*\*/);
      const title = titleMatch ? titleMatch[1] : `Generated Content Section ${index + 1}`;
      
      const contentBlock = titleMatch ? trimmedSection.substring(titleMatch[0].length).trim() : trimmedSection;

      const isCodeBlock = title.toLowerCase().includes('landing page code');
      if (isCodeBlock) {
        const codeMatch = contentBlock.match(/```html([\s\S]*)```/);
        const code = codeMatch ? codeMatch[1].trim() : "Could not parse HTML code.";
        return (
          <div key={index} className="mt-6">
            <h3 className="text-lg font-semibold border-b-2 pb-2 mb-3 text-gray-700">{title}</h3>
            <div className="relative">
              <code>{code}</code>
              <button className="copy-button" onClick={() => copyToClipboard(code, 'HTML Code')}>Copy</button>
            </div>
          </div>
        );
      }
      
      return (
        <div key={index} className="mt-6">
          <h3 className="text-lg font-semibold border-b-2 pb-2 mb-3 text-gray-700">{title}</h3>
          <pre>{contentBlock}</pre>
        </div>
      );
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg flex-1 min-h-[400px]">
      <h2 className="text-xl font-bold mt-0 border-b-2 pb-3 mb-3 text-gray-800">Results</h2>
      <div className="results-container bg-gray-50 border rounded-md p-4 max-h-[70vh] overflow-y-auto">
        {analysisResults && !generatedContent && (
          <div>
            <h3 className="text-lg font-semibold text-gray-700">Trend Analysis for "{analysisResults.niche}"</h3>
            <p className="mt-2"><strong>Forecast Summary:</strong> {analysisResults.forecast_summary}</p>
            <strong className="block mt-4">Top Opportunities:</strong>
            <ul className="list-disc list-inside mt-2 space-y-1">{analysisResults.top_opportunities.map((opp, i) => <li key={i}>{opp}</li>)}</ul>
            <strong className="block mt-4">Top Trends:</strong>
            <ul className="list-disc list-inside mt-2 space-y-1">{analysisResults.trends.map(trend => <li key={trend.id}>{trend.title} <span className="text-gray-500 text-sm">({trend.source})</span></li>)}</ul>
          </div>
        )}
        {generatedContent && <ContentViewer content={generatedContent.content} />}
        {!analysisResults && !generatedContent && <p className="text-gray-500">Your analysis and generated content will appear here.</p>}
      </div>
    </div>
  );
};

const HistoryPanel = ({ history }) => (
  <div className="bg-white p-6 rounded-lg shadow-lg">
    <h2 className="text-xl font-bold mt-0 mb-4 text-gray-800">Recent Activity</h2>
    {history.length === 0 ? <p className="text-gray-500">No recent activity.</p> : (
      <ul className="space-y-4">
        {history.map(item => (
          <li key={item.id} className="border-b pb-4 last:border-b-0">
            <div className="font-semibold text-gray-800">{item.title}</div>
            <div className="text-sm text-gray-500 capitalize">{item.niche} | {item.content_type.replace(/_/g, ' ')}</div>
          </li>
        ))}
      </ul>
    )}
  </div>
);

// --- Main App Component ---
function App() {
  const [niche, setNiche] = useState('fitness');
  const [contentType, setContentType] = useState('social_post');
  const [loading, setLoading] = useState({ isAnalyzing: false, isGenerating: false });
  const [analysisResults, setAnalysisResults] = useState(null);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [history, setHistory] = useState([]);

  const handleAnalyze = async () => {
    if (!niche) {
      toast.error('Please select a niche first.');
      return;
    }
    setLoading({ isAnalyzing: true, isGenerating: false });
    setAnalysisResults(null);
    setGeneratedContent(null);
    try {
      const response = await axios.post(`${API_URL}/api/niche/analyze`, { niche });
      setAnalysisResults(response.data);
      toast.success(`Successfully analyzed the ${niche} niche!`);
    } catch (error) {
      console.error("Error analyzing niche:", error);
      toast.error(error.response?.data?.detail || 'Failed to analyze niche. Please try again.');
    } finally {
      setLoading({ isAnalyzing: false, isGenerating: false });
    }
  };

  const handleGenerate = async () => {
    if (!analysisResults) {
      toast.error('Please analyze a niche first.');
      return;
    }
    setLoading({ ...loading, isGenerating: true });
    setGeneratedContent(null);
    const trendTitles = analysisResults.trends.map(t => t.title);
    try {
      const response = await axios.post(`${API_URL}/api/content/generate`, {
        niche: niche,
        trend_data: trendTitles,
        content_type: contentType
      });
      const newContent = response.data;
      setGeneratedContent(newContent);
      setHistory(prevHistory => [newContent, ...prevHistory].slice(0, 5));
      toast.success('Content generated successfully!');
    } catch (error) {
      console.error("Error generating content:", error);
      toast.error(error.response?.data?.detail || 'Failed to generate content. Please try again.');
    } finally {
      setLoading({ isAnalyzing: false, isGenerating: false });
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      <Toaster position="top-center" reverseOrder={false} />
      <Header />
      <main className="p-4 sm:p-8">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 flex flex-col gap-8">
            <NicheSelector
              niche={niche}
              setNiche={setNiche}
              contentType={contentType}
              setContentType={setContentType}
              handleAnalyze={handleAnalyze}
              handleGenerate={handleGenerate}
              loading={loading}
              analysisResults={analysisResults}
            />
            <ResultsDisplay
              analysisResults={analysisResults}
              generatedContent={generatedContent}
            />
          </div>
          <div className="lg:col-span-1">
            <HistoryPanel history={history} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;