// file: frontend/src/pages/LandingPage.js

import React from 'react';
import { Link } from 'react-router-dom';
import { Brain, Zap, Target } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Header */}
      <header className="bg-white shadow-sm p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Brain size={32} className="text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-800">NicheStack AI</h1>
          </div>
          <nav className="flex items-center gap-6">
            <Link to="/about" className="text-gray-600 hover:text-indigo-600 font-medium">About</Link>
            <Link to="/contact" className="text-gray-600 hover:text-indigo-600 font-medium">Contact</Link>
            <Link to="/app" className="bg-indigo-600 text-white font-semibold px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
              Launch App Free
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto text-center py-20 px-4">
        <h2 className="text-5xl font-extrabold text-gray-900 leading-tight">
          Your AI Co-Pilot for Niche Business Success
        </h2>
        <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
          From idea generation to content creation and market strategy, NicheStack AI provides the tools you need to discover, build, and grow your online business—all for free.
        </p>
        <Link to="/app" className="mt-10 inline-block bg-indigo-600 text-white font-bold text-lg px-10 py-4 rounded-lg hover:bg-indigo-700 transition-transform transform hover:scale-105">
          Start Building for Free
        </Link>
      </main>

      {/* Features Section */}
      <section className="bg-white py-20 px-4">
        <div className="container mx-auto grid md:grid-cols-3 gap-12 text-center">
          <div className="flex flex-col items-center">
            <div className="bg-indigo-100 p-4 rounded-full">
              <Target size={32} className="text-indigo-600" />
            </div>
            <h3 className="mt-4 text-xl font-bold">Discover Niches</h3>
            <p className="mt-2 text-gray-600">Uncover profitable business ideas backed by real-time data from Google Trends, Reddit, and Quora.</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="bg-indigo-100 p-4 rounded-full">
              <Zap size={32} className="text-indigo-600" />
            </div>
            <h3 className="mt-4 text-xl font-bold">Create Instantly</h3>
            <p className="mt-2 text-gray-600">Generate a complete content package—from SEO blogs to viral social posts—in seconds.</p>
          </div>
          <div className="flex flex-col items-center">
            <div className="bg-indigo-100 p-4 rounded-full">
              <Brain size={32} className="text-indigo-600" />
            </div>
            <h3 className="mt-4 text-xl font-bold">Strategize Like a Pro</h3>
            <p className="mt-2 text-gray-600">Get data-driven SEO strategies, marketing funnels, and e-commerce intelligence to dominate your market.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto text-center">
          <p>© {new Date().getFullYear()} NicheStack AI. All rights reserved.</p>
          <div className="mt-4 flex justify-center gap-6">
            <Link to="/privacy" className="hover:text-indigo-400">Privacy Policy</Link>
            <Link to="/contact" className="hover:text-indigo-400">Contact</Link>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;