import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import { Target, Search, Wand2, TrendingUp, Copy, Brain, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './App.css'; // Your custom styles

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// --- Reusable Components with Tailwind CSS ---

const Header = () => (
  <header className="bg-white shadow-md p-4 flex items-center gap-4">
    <Target size={32} className="text-indigo-600" />
    <h1 className="text-2xl font-bold text-gray-800">Oracle Engine</h1>
  </header>
);

const StatCard = ({ title, value, icon: Icon }) => (
  <div className="bg-white p-6 rounded-lg shadow-lg flex items-center justify-between">
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

// THIS IS THE CORRECTED, DEFENSIVE ResultsDisplay COMPONENT
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

  // Defensive check for chart data
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
        {/* Defensive check for opportunities */}
        <ol className="list-decimal list-inside space-y-2 text-gray-600 max-h-60 overflow-y-auto">
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
    // This component remains the same, but you can also add defensive checks here if needed.
    // For now, it's less critical as it only renders when `generatedContent` is not null.
};


// --- Main App Component ---
function App() {
  const [niche, setNiche] = useState('AI-powered SaaS');
  const [subNiche, setSubNiche] = useState('sales automation, copywriting tools');
  const [loading, setLoading] = useState({ isAnalyzing: false, isGenerating: false });
  const [analysisResults, setAnalysisResults] = useState(null);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [stats, setStats] = useState({ total_trends_monitored: 0, content_pieces_generated: 0, active_niches: [] });

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const handleAnalyze = async () => {
    if (!niche.trim()) {
      toast.error('Please enter a niche.');
      return;
    }
    // CORRECTED: Only update the relevant loading state
    setLoading(prev => ({ ...prev, isAnalyzing: true }));
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
      // CORRECTED: Display the specific error message from the backend
      toast.error(error.response?.data?.detail || 'An unexpected error occurred during analysis.');
    } finally {
      // CORRECTED: Only update the relevant loading state
      setLoading(prev => ({ ...prev, isAnalyzing: false }));
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
      fetchDashboardStats();
    } catch (error) {
      console.error("Error generating content:", error);
      toast.error(error.response?.data?.detail || 'Failed to generate content.');
    } finally {
      setLoading(prev => ({ ...prev, isGenerating: false }));
    }
  };
  
  // The JSX for the main App component remains the same
  return (
    <div className="min-h-screen bg-gray-100">
      <Toaster position="top-center" reverseOrder={false} />
      <Header />
      <main className="p-4 sm:p-8">
        <div className="max-w-7xl mx-auto flex flex-col gap-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard title="Trends Monitored" value={stats.total_trends_monitored} icon={TrendingUp} />
            <StatCard title="Content Generated" value={stats.content_pieces_generated} icon={Copy} />
            <StatCard title="Active Niches" value={stats.active_niches.length} icon={Target} />
            <StatCard title="System Status" value={"Operational"} icon={Activity} />
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1">
              <NicheInput
                niche={niche}
                setNiche={setNiche}
                subNiche={subNiche}
                setSubNiche={setSubNiche}
                handleAnalyze={handleAnalyze}
                loading={loading}
              />
            </div>
            <div className="lg:col-span-2">
              <ResultsDisplay
                analysisResults={analysisResults}
                handleGenerate={handleGenerate}
                loading={loading}
              />
            </div>
          </div>
          
          {generatedContent && <GeneratedContentDisplay generatedContent={generatedContent} />}

        </div>
      </main>
    </div>
  );
}

export default App;