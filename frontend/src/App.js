import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrendingUp, Zap, Target, Brain, Copy, MessageSquare, Star, Activity, Clock, Users } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [niche, setNiche] = useState('');
  const [keywords, setKeywords] = useState('');
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [contentType, setContentType] = useState('ad_copy');
  const [stats, setStats] = useState({
    total_trends_monitored: 0,
    content_pieces_generated: 0,
    active_niches: [],
    system_status: 'operational'
  });

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const analyzeNiche = async () => {
    if (!niche.trim()) {
      toast.error('Please enter a niche to analyze');
      return;
    }

    setLoading(true);
    try {
      const keywordArray = keywords.split(',').map(k => k.trim()).filter(k => k);
      const response = await axios.post(`${API}/niche/analyze`, {
        niche: niche.trim(),
        keywords: keywordArray
      });

      setTrends(response.data.trends);
      toast.success(`Found ${response.data.trends.length} trends for ${niche}!`);
      setActiveTab('trends');
    } catch (error) {
      console.error('Error analyzing niche:', error);
      toast.error('Failed to analyze niche. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const generateContent = async (type) => {
    if (trends.length === 0) {
      toast.error('Please analyze a niche first to get trends');
      return;
    }

    setLoading(true);
    try {
      const trendTitles = trends.slice(0, 5).map(t => t.title);
      const response = await axios.post(`${API}/content/generate`, {
        niche: niche,
        trend_data: trendTitles,
        content_type: type
      });

      setGeneratedContent(response.data);
      toast.success(`Generated ${type.replace('_', ' ')} content!`);
      setActiveTab('content');
      fetchDashboardStats(); // Update stats
    } catch (error) {
      console.error('Error generating content:', error);
      toast.error('Failed to generate content. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const getTrendChartData = () => {
    return trends.slice(0, 6).map((trend, index) => ({
      name: trend.title.substring(0, 20) + '...',
      score: Math.round(trend.trend_score * 100),
      velocity: Math.round(trend.velocity * 100)
    }));
  };

  const NicheInput = () => (
    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
      <div className="flex items-center gap-3 mb-6">
        <Target className="w-8 h-8 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-800">Target Your Niche</h2>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Niche/Market Focus
          </label>
          <input
            type="text"
            value={niche}
            onChange={(e) => setNiche(e.target.value)}
            placeholder="e.g., fitness, crypto, SaaS, ecommerce, marketing"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional Keywords (optional)
          </label>
          <input
            type="text"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="keyword1, keyword2, keyword3"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <button
          onClick={analyzeNiche}
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Analyzing...
            </>
          ) : (
            <>
              <Brain className="w-5 h-5" />
              Analyze Niche
            </>
          )}
        </button>
      </div>
      
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="font-medium text-blue-800 mb-2">🚀 Popular Niches:</h3>
        <div className="flex flex-wrap gap-2">
          {['fitness', 'crypto', 'SaaS', 'ecommerce', 'marketing', 'real estate'].map(nicheOption => (
            <button
              key={nicheOption}
              onClick={() => setNiche(nicheOption)}
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
            >
              {nicheOption}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const TrendsView = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-green-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Trend Analysis: {niche}</h2>
              <p className="text-gray-600">Real-time trend monitoring and predictions</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => generateContent('ad_copy')}
              disabled={loading}
              className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors flex items-center gap-2"
            >
              <Copy className="w-4 h-4" />
              Generate Ads
            </button>
            <button
              onClick={() => generateContent('social_post')}
              disabled={loading}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
            >
              <MessageSquare className="w-4 h-4" />
              Social Posts
            </button>
          </div>
        </div>

        {trends.length > 0 && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4">Trend Performance</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getTrendChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" fill="#3B82F6" name="Trend Score" />
                <Bar dataKey="velocity" fill="#10B981" name="Velocity" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="grid gap-4">
          {trends.map((trend, index) => (
            <div key={trend.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                      #{index + 1}
                    </span>
                    <h3 className="font-semibold text-gray-800">{trend.title}</h3>
                  </div>
                  <p className="text-gray-600 mb-3">{trend.content}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Activity className="w-4 h-4" />
                      Score: {Math.round(trend.trend_score * 100)}%
                    </span>
                    <span className="flex items-center gap-1">
                      <Zap className="w-4 h-4" />
                      Velocity: {Math.round(trend.velocity * 100)}%
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {trend.source}
                    </span>
                  </div>
                </div>
                <div className="ml-4">
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-600">
                      {Math.round((trend.trend_score * trend.velocity) * 100)}
                    </div>
                    <div className="text-xs text-gray-500">Opportunity Score</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const ContentView = () => (
    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
      <div className="flex items-center gap-3 mb-6">
        <Star className="w-8 h-8 text-purple-600" />
        <h2 className="text-2xl font-bold text-gray-800">Generated Content</h2>
      </div>

      {generatedContent ? (
        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg border border-purple-200">
            <div>
              <h3 className="font-semibold text-purple-800">{generatedContent.title}</h3>
              <p className="text-purple-600 text-sm">
                Confidence: {Math.round(generatedContent.confidence_score * 100)}% | 
                Type: {generatedContent.content_type.replace('_', ' ')} | 
                Niche: {generatedContent.niche}
              </p>
            </div>
            <button
              onClick={() => copyToClipboard(generatedContent.content)}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
            >
              <Copy className="w-4 h-4" />
              Copy All
            </button>
          </div>

          <div className="border border-gray-200 rounded-lg p-6">
            <h4 className="font-medium text-gray-800 mb-4">Generated Content:</h4>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                {generatedContent.content}
              </pre>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => generateContent('ad_copy')}
              disabled={loading}
              className="bg-orange-500 text-white px-6 py-3 rounded-lg hover:bg-orange-600 transition-colors flex items-center gap-2"
            >
              <Copy className="w-5 h-5" />
              Generate Ad Copy
            </button>
            <button
              onClick={() => generateContent('social_post')}
              disabled={loading}
              className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
            >
              <MessageSquare className="w-5 h-5" />
              Generate Social Posts
            </button>
            <button
              onClick={() => generateContent('affiliate_review')}
              disabled={loading}
              className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
            >
              <Star className="w-5 h-5" />
              Generate Review
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-600 mb-2">No Content Generated Yet</h3>
          <p className="text-gray-500">Analyze a niche and generate content from the trends view</p>
        </div>
      )}
    </div>
  );

  const DashboardView = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Trends Monitored</p>
              <p className="text-2xl font-bold text-gray-800">{stats.total_trends_monitored}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Content Generated</p>
              <p className="text-2xl font-bold text-gray-800">{stats.content_pieces_generated}</p>
            </div>
            <Copy className="w-8 h-8 text-green-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Active Niches</p>
              <p className="text-2xl font-bold text-gray-800">{stats.active_niches.length}</p>
            </div>
            <Target className="w-8 h-8 text-purple-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">System Status</p>
              <p className="text-lg font-semibold text-green-600 capitalize">{stats.system_status}</p>
            </div>
            <Activity className="w-8 h-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Main Input */}
      <NicheInput />
      
      {/* Features Overview */}
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Oracle Engine Features</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center p-6">
            <Brain className="w-12 h-12 text-blue-600 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-800 mb-2">AI-Powered Analysis</h3>
            <p className="text-gray-600 text-sm">Advanced trend monitoring using Google Trends and AI prediction algorithms</p>
          </div>
          <div className="text-center p-6">
            <Zap className="w-12 h-12 text-green-600 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-800 mb-2">Real-time Generation</h3>
            <p className="text-gray-600 text-sm">Instant content creation using OpenAI GPT-4o and Gemini 2.5 Flash</p>
          </div>
          <div className="text-center p-6">
            <Target className="w-12 h-12 text-purple-600 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-800 mb-2">Niche Targeting</h3>
            <p className="text-gray-600 text-sm">Specialized content for your specific market and audience</p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">Oracle Engine</h1>
                <p className="text-xs text-gray-600">AI-Powered Marketing Intelligence</p>
              </div>
            </div>
            
            <nav className="flex gap-1">
              {[
                { id: 'dashboard', label: 'Dashboard', icon: Activity },
                { id: 'trends', label: 'Trends', icon: TrendingUp },
                { id: 'content', label: 'Content', icon: MessageSquare }
              ].map(tab => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                      activeTab === tab.id 
                        ? 'bg-blue-100 text-blue-700 font-medium' 
                        : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <DashboardView />}
        {activeTab === 'trends' && <TrendsView />}
        {activeTab === 'content' && <ContentView />}
      </main>
    </div>
  );
}

export default App;