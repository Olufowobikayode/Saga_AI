// file: frontend/src/pages/PrivacyPolicyPage.js

import React from 'react';
import { Link } from 'react-router-dom';
import { Brain } from 'lucide-react';

const PrivacyPolicyPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Consistent Header */}
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

      {/* Main Content */}
      <main className="container mx-auto p-8 bg-white mt-8 rounded-lg shadow-lg max-w-4xl prose lg:prose-lg">
        <h1>Privacy Policy for NicheStack AI</h1>
        <p><strong>Last Updated:</strong> {new Date().toLocaleDateString()}</p>

        <h2>1. Introduction</h2>
        <p>
          Welcome to NicheStack AI ("we," "our," or "us"). We are committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website and use our application (our "Service").
        </p>

        <h2>2. Information We Collect</h2>
        <p>
          We may collect information about you in a variety of ways. The information we may collect on the Service includes:
        </p>
        <ul>
          <li><strong>Usage Data:</strong> We may automatically collect information about your access to and use of the Service, such as your IP address, browser type, pages viewed, and the dates/times of your visits.</li>
          <li><strong>Cookies and Web Beacons:</strong> We may use cookies and similar tracking technologies to help customize the Service and improve your experience.</li>
        </ul>

        <h2>3. Use of Your Information</h2>
        <p>
          Having accurate information permits us to provide you with a smooth, efficient, and customized experience. Specifically, we may use information collected about you via the Service to:
        </p>
        <ul>
            <li>Improve our Service and offerings.</li>
            <li>Monitor and analyze usage and trends to improve your experience.</li>
            <li>Deliver targeted advertising, promotions, and other information regarding our Service.</li>
        </ul>

        <h2>4. Third-Party Advertising (Google AdSense)</h2>
        <p>
          We use third-party advertising companies, such as Google AdSense, to serve ads when you visit the Service. These companies may use information about your visits to this and other websites that are contained in web cookies in order to provide advertisements about goods and services of interest to you.
        </p>
        <p>
          Google's use of the DART cookie enables it to serve ads to our users based on their visit to our sites and other sites on the Internet. Users may opt out of the use of the DART cookie by visiting the Google ad and content network privacy policy.
        </p>
        
        <h2>5. Security of Your Information</h2>
        <p>
          We use administrative, technical, and physical security measures to help protect your personal information. While we have taken reasonable steps to secure the personal information you provide to us, please be aware that despite our efforts, no security measures are perfect or impenetrable.
        </p>
        
        <h2>6. Contact Us</h2>
        <p>
          If you have questions or comments about this Privacy Policy, please contact us through our <Link to="/contact" className="text-indigo-600 hover:underline">Contact Page</Link>.
        </p>
      </main>

      {/* Consistent Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="container mx-auto text-center">
          <p>© {new Date().getFullYear()} NicheStack AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default PrivacyPolicyPage;