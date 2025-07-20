import React from 'react';
import { Link } from 'react-router-dom';
import { Brain } from 'lucide-react';

const AboutPage = () => (
  <div className="min-h-screen bg-gray-50">
    <header className="bg-white shadow-sm p-4">
        <div className="container mx-auto flex justify-between items-center">
          <Link to="/" className="flex items-center gap-3">
            <Brain size={32} className="text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-800">NicheStack AI</h1>
          </Link>
          <Link to="/app" className="bg-indigo-600 text-white font-semibold px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
              Launch App
          </Link>
        </div>
    </header>
    <main className="container mx-auto p-8 bg-white mt-8 rounded-lg shadow-lg max-w-4xl">
      <h2 className="text-4xl font-bold text-gray-900">About NicheStack AI</h2>
      <p className="mt-6 text-lg text-gray-600">
        Our mission is to empower the next generation of solopreneurs, creators, and small business owners by providing a powerful, AI-driven co-pilot for success. We believe that a great idea backed by data and executed with a clear strategy is unstoppable.
      </p>
      <p className="mt-4 text-lg text-gray-600">
        NicheStack AI was born from the struggle of navigating the overwhelming process of starting and growing an online business. We've automated the most difficult parts—market research, content creation, and strategic planning—so you can focus on what you do best: building your brand.
      </p>
    </main>
  </div>
);

export default AboutPage;