// file: frontend/src/pages/AppPage.js

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import { Link } from 'react-router-dom';
import { Home, Lightbulb, FileText, ShoppingCart, BarChart2, Brain, Send, PenSquare, Loader2, Copy } from 'lucide-react';
import '../App.css'; // Your custom styles

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// --- Reusable Components (Defined within this file for simplicity) ---

const Header = () => (
    <header className="bg-white shadow-md p-4 flex items-center justify-between z-10">
        <div className="flex items-center gap-4">
            <Brain size={32} className="text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-800">NicheStack AI App</h1>
        </div>
        <Link to="/" className="flex items-center gap-2 text-gray-600 hover:text-indigo-600 font-semibold transition-colors">
            <Home size={18} />
            <span>Back to Homepage</span>
        </Link>
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
                    value={subNiche} onChange={(e) => setSubNiche(e.target.value)} placeholder="e.g., sales automation" />
            </div>
            <button
                className="w-full flex items-center justify-center gap-2 p-3 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 disabled:bg-gray-400"
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
                    <Loader2 className="h-12 w-12 text-indigo-600 animate-spin mx-auto" />
                    <p className="mt-4 text-gray-600 font-semibold">Analyzing niche...</p>
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
                </div>
            </div>
        );
    }
    
    const contentTypes = [
        { id: 'facebook_post', label: 'Facebook Post' }, { id: 'twitter_thread', label: 'X (Twitter)' },
        { id: 'linkedin_article', label: 'LinkedIn Article' }, { id: 'seo_blog_post', label: 'SEO Blog' },
        { id: 'ad_copy', label: 'Ad Copy' }, { id: 'affiliate_review', label: 'Affiliate Review' },
        { id: 'print_on_demand', label: 'Print on Demand' }, { id: 'ecommerce_product', label: 'E-commerce' }
    ];

    const chartData = analysisResults?.trends?.slice(0, 6).map(t => ({
        name: t.title.replace('Live Trend: ', '').split(' ').slice(0, 2).join(' '),
        score: Math.round(t.trend_score * 100)
    })) || [];

    return (
        <div className="bg-white p-6 rounded-lg shadow-lg flex-1">
            <h2 className="text-2xl font-bold text-gray-800">Analysis for "{analysisResults?.niche}"</h2>
            <p className="mt-2 text-gray-600">{analysisResults?.forecast_summary}</p>
            
            <div className="mt-6">
                <h3 className="text-xl font-semibold text-gray-700 mb-4">Top Opportunities</h3>
                <ol className="list-decimal list-inside space-y-2 text-gray-600 max-h-60 overflow-y-auto pr-2">
                    {analysisResults?.top_opportunities?.map((opp, i) => <li key={i}>{opp}</li>) || <li>No opportunities found.</li>}
                </ol>
            </div>

            {chartData.length > 0 && (
                <div className="mt-6">
                    <h3 className="text-xl font-semibold text-gray-700 mb-4">Top Trend Performance</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" angle={-10} textAnchor="end" height={50} />
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
    // ... (This component is correct, no changes needed)
};

const DetailsPanel = ({ view, data, loading }) => {
    // ... (This component is correct, no changes needed)
};

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
        // ... (This function is correct, no changes needed)
    };

    const handleAnalyze = async () => {
        // ... (This function is correct, no changes needed)
    };

    const handleGenerate = async (contentType) => {
        // ... (This function is correct, no changes needed)
    };
  
    return (
        <div className="min-h-screen bg-gray-100">
            <Header />
            <main className="p-4 sm:p-8">
                <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-8">
                    <div className="lg:w-1/3 flex flex-col gap-8">
                        <NicheInput
                            niche={niche}
                            setNiche={setNiche}
                            subNiche={subNiche}
                            setSubNiche={setSubNiche}
                            handleAnalyze={handleAnalyze}
                            loading={loading}
                        />
                         <DetailsPanel view={detailsView} data={detailsData} loading={loading.isFetchingDetails} />
                    </div>
                    <div className="lg:w-2/3 flex flex-col gap-8">
                         <ResultsDisplay
                            analysisResults={analysisResults}
                            handleGenerate={handleGenerate}
                            loading={loading}
                        />
                        {generatedContent && <GeneratedContentDisplay generatedContent={generatedContent} />}
                    </div>
                </div>
            </main>
        </div>
    );
}

export default AppPage;