// file: frontend/src/pages/AppPage.js

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import { Target, Search, Wand2, TrendingUp, Copy, Brain, Activity, List } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import '../App.css'; // Import custom styles for recharts and code blocks

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// --- Reusable Components (Defined within this file for simplicity) ---

const Header = () => (
  <header className="bg-white shadow-md p-4 flex items-center gap-4">
    <Target size={32} className="text-indigo-600" />
    <h1 className="text-2xl font-bold text-gray-800">NicheStack AI - App</h1>
  </header>
);

const StatCard = ({ title, value, icon: Icon, onClick, active }) => (
  <div onClick={onClick} className={`bg-white p-6 rounded-lg shadow-lg flex items-center justify-between transition-all duration-200 ${onClick ? 'cursor-pointer hover:shadow-xl hover:-translate-y-1' : ''} ${active ? 'ring-2 ring-indigo-500' : ''}`}>
    <div>
      <p className="text-sm text-gray-500 font-medium">{title}</p>
      <p className="text-3xl font-bold text-gray-800">{value}</p>
    </div>
    <div className="bg-indigo-100 p-3 rounded-full">
      <Icon className="h-6 w-6 text-indigo-600" />
    </div>
  </div>
);

const NicheInput = ({ niche, setNiche, subNiche, setSubNiche, handleAnalyze, loading }) => (
  <div className="bg-white p-6 rounded-lg shadow-lg">
    <div className="flex flex-col gap-4">
      <div>
        <label htmlFor="niche-input" className="block font-semibold mb-2 text-gray-700">Niche / Market</label>
        <input id="niche-input" type="text" className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          value={niche} onChange={(e) => setNiche(e.target.value)} placeholder="e.g., AI-powered SaaS" />
      </div>
      <div>
        <label htmlFor="subniche-input" className="block font-semibold mb-2 text-gray-700">Sub-Niche / Keywords (Optional)</label>
        <input id="subniche-input" type="text" className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
          value={subNiche} onChange={(e) => setSubNiche(e.target.value)} placeholder="e.g., sales automation, copywriting tools" />
      </div>
      <button
        className="w-full flex items-center justify-center gap-2 p-3 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
        onClick={handleAnalyze} disabled={loading.isAnalyzing}>
        <Brain size={18} />
        {loading.isAnalyzing ? 'Analyzing...' : 'Analyze Niche'}
      </button>
    </div>
  </div>
);

const ResultsDisplay = ({ analysisResults, handleGenerate, loading }) => {
  if (loading.isAnalyzing) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-lg flex-1 min-h-[400px] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 font-semibold">Analyzing niche... this may take a moment.</p>
        </div>
      </div>
    );
  }

  if (!analysisResults) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-lg flex-1 min-h-[400px] flex items-center justify-center">
        <div className="text-center text-gray-500">
          <Brain size={48} className="mx-auto mb-4" />
          <p className="font-semibold">Your results will appear here.</p>
          <p>Start by analyzing a niche.</p>
        </div>
      </div>
    );
  }
  
  const contentTypes = [
    { id: 'facebook_post', label: 'Facebook Post' }, { id: 'twitter_thread', label: 'X (Twitter) Thread' },
    { id: 'linkedin_article', label: 'LinkedIn Article' }, { id: 'seo_blog_post', label: 'SEO Blog Post' },
    { id: 'ad_copy', label: 'Ad Copy' }, { id: 'affiliate_review', label: 'Affiliate Review' },
    { id: 'print_on_demand', label: 'Print on Demand' }, { id: 'ecommerce_product', label: 'E-commerce Product' }
  ];

  const chartData = analysisResults?.trends?.slice(0, 6).map(t => ({
    name: t.title.split(' ').slice(0, 3).join(' ') + '...',
    score: Math.round(t.trend_score * 100)
  })) || [];

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg flex-1">
      <h2 className="text-2xl font-bold text-gray-800">Analysis for "{analysisResults.niche}"</h2>
      <p className="mt-2 text-gray-600">{analysisResults.forecast_summary}</p>
      
      <div className="mt-6">
        <h3 className="text-xl font-semibold text-gray-700 mb-4">Top 20 Opportunities</h3>
        <ol className="list-decimal list-inside space-y-2 text-gray-600 max-h-60 overflow-y-auto pr-2">
          {analysisResults?.top_opportunities?.map((opp, i) => <li key={i}>{opp}</li>) || <li>No opportunities generated.</li>}
        </ol>
      </div>

      {chartData.length > 0 && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">Top Trend Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="score" fill="#4f46e5" name="Trend Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="mt-8 border-t pt-6">
        <h3 className="text-xl font-semibold text-gray-700 mb-4">Generate Content</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {contentTypes.map(({ id, label }) => (
            <button key={id} onClick={() => handleGenerate(id)} disabled={loading.isGenerating || !analysisResults?.trends?.length}
              className="p-3 bg-gray-100 text-gray-700 font-semibold rounded-md hover:bg-gray-200 disabled:bg-gray-400 disabled:text-white transition-colors text-sm text-center">
              {loading.isGenerating ? 'Working...' : label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

const GeneratedContentDisplay = ({ generatedContent }) => {
  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text);
    toast.success(`${type} copied to clipboard!`);
  };

  if (!generatedContent) return null;

  const sections = generatedContent.content.split('---').filter(section => section.trim() !== '');

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center border-b pb-4 mb-4">
        <h2 className="text-2xl font-bold text-gray-800 capitalize">{generatedContent.content_type.replace(/_/g, ' ')} for "{generatedContent.niche}"</h2>
        <button onClick={() => copyToClipboard(generatedContent.content, "Content")}
          className="flex items-center gap-2 p-2 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 text-sm">
          <Copy size={16} /> Copy All
        </button>
      </div>
      <div className="results-output">
        {sections.map((section, index) => {
          const trimmedSection = section.trim();
          const titleMatch = trimmedSection.match(/^\*\*(.*?):\*\*/);
          const title = titleMatch ? titleMatch[1] : `Content Section ${index + 1}`;
          const contentBlock = titleMatch ? trimmedSection.substring(titleMatch[0].length).trim() : trimmedSection;
          
          if (title.toLowerCase().includes('landing page code')) {
            const codeMatch = contentBlock.match(/```html([\s\S]*)```/);
            const code = codeMatch ? codeMatch[1].trim() : "Could not parse HTML code.";
            return (
              <div key={index} className="mt-4">
                <h3 className="text-lg font-semibold mb-2 text-gray-700">{title}</h3>
                <div className="relative"><code>{code}</code><button className="copy-button" onClick={() => copyToClipboard(code, 'HTML Code')}>Copy</button></div>
              </div>
            );
          }
          
          return (
            <div key={index} className="mt-4">
              <h3 className="text-lg font-semibold mb-2 text-gray-700">{title}</h3>
              <pre>{contentBlock}</pre>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const DetailsPanel = ({ view, data, loading }) => (
  <div className="bg-white p-6 rounded-lg shadow-lg">
    <h2 className="text-xl font-bold mt-0 mb-4 text-gray-800 capitalize flex items-center gap-2">
      <List size={20} />
      {view.replace(/_/g, ' ')}
    </h2>
    {loading ? (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-3 text-gray-500">Fetching data...</p>
      </div>
    ) : data.length === 0 ? (
      <p className="text-gray-500">No data to display.</p>
    ) : (
      <ul className="space-y-4 max-h-[65vh] overflow-y-auto pr-2">
        {data.map(item => (
          <li key={item._id || item.id} className="border-b pb-4 last:border-b-0">
            <div className="font-semibold text-gray-800">{item.title || item}</div>
            <div className="text-sm text-gray-500 capitalize">
              {view === 'all_trends' && `Source: ${item.source}`}
              {view === 'all_content' && `Niche: ${item.niche} | Type: ${item.content_type.replace(/_/g, ' ')}`}
              {view === 'active_niches' && `Niche`}
            </div>
          </li>
        ))}
      </ul>
    )}
  </div>
);


// --- Main App Page Component ---
function AppPage() {
  const [niche, setNiche] = useState('AI-powered SaaS');
  const [subNiche, setSubNiche] = useState('sales automation, copywriting tools');
  const [loading, setLoading] = useState({ isAnalyzing: false, isGenerating: false, isFetchingDetails: false });
  const [analysisResults, setAnalysisResults] = useState(null);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [stats, setStats] = useState({ total_trends_monitored: 0, content_pieces_generated: 0, active_niches: [] });
  
  const [detailsView, setDetailsView] = useState('active_niches');
  const [detailsData, setDetailsData] = useState([]);

  const fetchDashboardStats = useCallback(async (currentView) => {
    try {
      const response = await axios.get(`${API_URL}/api/dashboard/stats`);
      const newStats = response.data;
      setStats(newStats);
      if (currentView === 'active_niches') {
        setDetailsData((newStats.active_niches || []).map(niche => ({ title: niche, id: niche })));
      }
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  }, []);

  useEffect(() => {
    fetchDashboardStats(detailsView);
  }, [fetchDashboardStats, detailsView]);

  const handleStatCardClick = async (viewType) => {
    if (!viewType) return;
    setDetailsView(viewType);
    setLoading(prev => ({ ...prev, isFetchingDetails: true }));
    setDetailsData([]);

    let endpoint = '';
    let dataKey = '';

    if (viewType === 'active_niches') {
        setDetailsData((stats.active_niches || []).map(niche => ({ title: niche, id: niche })));
        setLoading(prev => ({ ...prev, isFetchingDetails: false }));
        return;
    }

    if (viewType === 'all_trends') {
        endpoint = '/api/trends/all';
        dataKey = 'all_trends';
    } else if (viewType === 'all_content') {
        endpoint = '/api/content/all';
        dataKey = 'all_content';
    } else {
        setLoading(prev => ({ ...prev, isFetchingDetails: false }));
        return;
    }

    try {
      const response = await axios.get(`${API_URL}${endpoint}`);
      setDetailsData(response.data[dataKey] || []);
    } catch (error) {
      toast.error(`Could not fetch data. Please try again.`);
      console.error(`Error fetching ${viewType}:`, error);
    } finally {
      setLoading(prev => ({ ...prev, isFetchingDetails: false }));
    }
  };

  const handleAnalyze = async () => {
    if (!niche.trim()) {
      toast.error('Please enter a niche.');
      return;
    }
    setLoading({ isAnalyzing: true, isGenerating: false, isFetchingDetails: false });
    setAnalysisResults(null);
    setGeneratedContent(null);
    try {
      const keywordsArray = subNiche.split(',').map(k => k.trim()).filter(k => k);
      const response = await axios.post(`${API_URL}/api/niche/analyze`, { niche: niche.trim(), keywords: keywordsArray });
      setAnalysisResults(response.data);
      if (response.data?.trends?.length > 0) {
        toast.success(`Analysis complete for "${niche}"!`);
      } else {
        toast.error(`No live trends found for "${niche}". Please try a broader niche.`);
      }
    } catch (error) {
      console.error("Error analyzing niche:", error);
      toast.error(error.response?.data?.detail || 'An unexpected error occurred during analysis.');
    } finally {
      setLoading(prev => ({...prev, isAnalyzing: false}));
    }
  };

  const handleGenerate = async (contentType) => {
    if (!analysisResults || !analysisResults.trends || analysisResults.trends.length === 0) {
      toast.error('Cannot generate content without trend data. Please analyze a niche first.');
      return;
    }
    setLoading(prev => ({ ...prev, isGenerating: true }));
    setGeneratedContent(null);
    const trendTitles = analysisResults.trends.map(t => t.title);
    try {
      const response = await axios.post(`${API_URL}/api/content/generate`, {
        niche: niche,
        trend_data: trendTitles,
        content_type: contentType
      });
      setGeneratedContent(response.data);
      toast.success(`${contentType.replace(/_/g, ' ')} generated successfully!`);
      fetchDashboardStats(detailsView);
    } catch (error) {
      console.error("Error generating content:", error);
      toast.error(error.response?.data?.detail || 'Failed to generate content.');
    } finally {
      setLoading(prev => ({...prev, isGenerating: false}));
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="p-4 sm:p-8">
        <div className="max-w-7xl mx-auto flex flex-col gap-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard title="Trends Monitored" value={stats.total_trends_monitored} icon={TrendingUp} onClick={() => handleStatCardClick('all_trends')} active={detailsView === 'all_trends'} />
            <StatCard title="Content Generated" value={stats.content_pieces_generated} icon={Copy} onClick={() => handleStatCardClick('all_content')} active={detailsView === 'all_content'} />
            <StatCard title="Active Niches" value={stats.active_niches.length} icon={Target} onClick={() => handleStatCardClick('active_niches')} active={detailsView === 'active_niches'} />
            <StatCard title="System Status" value={"Operational"} icon={Activity} />
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 flex flex-col gap-8">
              <NicheInput
                niche={niche}
                setNiche={setNiche}
                subNiche={subNiche}
                setSubNiche={setSubNiche}
                handleAnalyze={handleAnalyze}
                loading={loading}
              />
              <ResultsDisplay
                analysisResults={analysisResults}
                handleGenerate={handleGenerate}
                loading={loading}
              />
            </div>
            <div className="lg:col-span-1">
              <DetailsPanel view={detailsView} data={detailsData} loading={loading.isFetchingDetails} />
            </div>
          </div>
          
          {generatedContent && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                    <GeneratedContentDisplay generatedContent={generatedContent} />
                </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}

export default AppPage;