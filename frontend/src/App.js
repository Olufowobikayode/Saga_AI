import React, { useState } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import { Target, Search, Wand2 } from 'lucide-react';

// Import the stylesheet
import './App.css';

// Setup the base URL for the API
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// --- Reusable Components Defined Within App.js ---

const Header = () => (
  <header className="header">
    <Target size={32} color="#2563eb" />
    <h1>Oracle Engine</h1>
  </header>
);

const NicheSelector = ({ niche, setNiche, contentType, setContentType, handleAnalyze, handleGenerate, loading, analysisResults }) => {
  const niches = ["Fitness", "Crypto", "SaaS", "Marketing", "E-commerce", "Health", "AI", "Real Estate"];
  const contentTypes = ["Social Post", "Ad Copy", "Affiliate Review", "Print on Demand", "E-commerce Product"];

  return (
    <div className="card">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div>
          <label htmlFor="niche-select" style={{ fontWeight: '600', marginBottom: '0.5rem', display: 'block' }}>
            1. Choose Your Niche
          </label>
          <select id="niche-select" className="select" value={niche} onChange={(e) => setNiche(e.target.value)}>
            {niches.map(n => <option key={n} value={n.toLowerCase()}>{n}</option>)}
          </select>
        </div>
        
        <button className="button" onClick={handleAnalyze} disabled={!niche || loading.isAnalyzing}>
          <Search size={18} />
          {loading.isAnalyzing ? 'Analyzing Niche...' : 'Analyze Niche'}
        </button>

        {analysisResults && (
          <>
            <div>
              <label htmlFor="content-type-select" style={{ fontWeight: '600', marginBottom: '0.5rem', display: 'block' }}>
                2. Select Content Type
              </label>
              <select id="content-type-select" className="select" value={contentType} onChange={(e) => setContentType(e.target.value)}>
                {contentTypes.map(type => <option key={type} value={type.toLowerCase().replace(/ /g, '_')}>{type}</option>)}
              </select>
            </div>
            <button className="button" onClick={handleGenerate} disabled={!contentType || loading.isGenerating}>
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
      const firstLine = trimmedSection.split('\n')[0];
      
      const isCodeBlock = (title) => title.toLowerCase().includes('landing page code');
      
      if (firstLine.includes('IF Content Type is')) {
        const title = firstLine.replace('### IF Content Type is', '').replace(':', '').trim().replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        const contentBlock = trimmedSection.substring(firstLine.length).trim();
        
        if (isCodeBlock(title)) {
          const codeMatch = contentBlock.match(/```html([\s\S]*)```/);
          const code = codeMatch ? codeMatch[1].trim() : "Could not parse HTML code.";
          return (
            <div key={index}>
              <h3>{title}</h3>
              <div style={{ position: 'relative' }}>
                <code>{code}</code>
                <button className="copy-button" onClick={() => copyToClipboard(code, 'HTML Code')}>Copy Code</button>
              </div>
            </div>
          );
        } else {
          return (
            <div key={index}>
              <h3>{title}</h3>
              <pre style={{ fontFamily: 'inherit', fontSize: 'inherit' }}>{contentBlock}</pre>
            </div>
          );
        }
      }
      return null;
    });
  };

  return (
    <div className="card" style={{ flex: 1 }}>
      <h2 style={{ marginTop: 0, borderBottom: '2px solid #f0f2f5', paddingBottom: '1rem' }}>Results</h2>
      <div className="results-container">
        {analysisResults && !generatedContent && (
          <div>
            <h3>Trend Analysis for "{analysisResults.niche}"</h3>
            <p><strong>Forecast Summary:</strong> {analysisResults.forecast_summary}</p>
            <strong>Top Opportunities:</strong>
            <ul>{analysisResults.top_opportunities.map((opp, i) => <li key={i}>{opp}</li>)}</ul>
            <strong>Top Trends:</strong>
            <ul>{analysisResults.trends.map(trend => <li key={trend.id}>{trend.title} (Source: {trend.source})</li>)}</ul>
          </div>
        )}
        {generatedContent && <ContentViewer content={generatedContent.content} />}
        {!analysisResults && !generatedContent && <p>Your analysis and generated content will appear here.</p>}
      </div>
    </div>
  );
};

const HistoryPanel = ({ history }) => (
  <div className="card">
    <h2 style={{ marginTop: 0 }}>Recent Activity</h2>
    {history.length === 0 ? <p>No recent activity.</p> : (
      <ul className="history-list">
        {history.map(item => (
          <li key={item.id} className="history-item">
            <div className="history-title">{item.title}</div>
            <div className="history-meta">{item.niche} | {item.content_type.replace(/_/g, ' ')}</div>
          </li>
        ))}
      </ul>
    )}
  </div>
);

// --- Main App Component ---
const App = () => {
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
    setLoading({ ...loading, isAnalyzing: true });
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
    if (!analysisResults || !contentType) {
      toast.error('Please analyze a niche and select a content type first.');
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
      setHistory(prevHistory => [newContent, ...prevHistory].slice(0, 10));
      toast.success('Content generated successfully!');
    } catch (error) {
      console.error("Error generating content:", error);
      toast.error(error.response?.data?.detail || 'Failed to generate content. Please try again.');
    } finally {
      setLoading({ isAnalyzing: false, isGenerating: false });
    }
  };

  return (
    <div className="app-container">
      <Toaster position="top-center" reverseOrder={false} />
      <Header />
      <main className="main-content">
        <div className="left-panel">
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
        <div className="right-panel">
          <HistoryPanel history={history} />
        </div>
      </main>
    </div>
  );
};

export default App;