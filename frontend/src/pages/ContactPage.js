// file: frontend/src/pages/ContactPage.js

import React from 'react';
import { Link } from 'react-router-dom';
import { Brain, Mail, MessageSquare } from 'lucide-react';

const ContactPage = () => {
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
      <main className="container mx-auto p-8 bg-white mt-8 rounded-lg shadow-lg max-w-4xl">
        <h2 className="text-4xl font-bold text-gray-900 text-center">Get In Touch</h2>
        <p className="mt-4 text-lg text-gray-600 text-center max-w-2xl mx-auto">
          We'd love to hear from you! Whether you have a question, feedback, or a partnership inquiry, here's how you can reach us.
        </p>

        <div className="mt-12 grid md:grid-cols-2 gap-8">
          {/* Contact Information */}
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-3">
                <Mail className="text-indigo-600" />
                Email Us
              </h3>
              <p className="mt-2 text-gray-600">
                For general inquiries, feedback, and support, please email us directly. We do our best to respond within 48 hours.
              </p>
              <a href="mailto:contact@nichestackai.com" className="text-lg text-indigo-600 font-semibold hover:underline">
                contact@nichestackai.com
              </a>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-3">
                <MessageSquare className="text-indigo-600" />
                Follow Us on X (Twitter)
              </h3>
              <p className="mt-2 text-gray-600">
                For the latest updates, feature announcements, and to join the conversation, follow our developer on X.
              </p>
              <a href="https://twitter.com/wikicathy" target="_blank" rel="noopener noreferrer" className="text-lg text-indigo-600 font-semibold hover:underline">
                @wikicathy
              </a>
            </div>
          </div>
          
          {/* Contact Form Placeholder */}
          <div>
            <h3 className="text-xl font-semibold text-gray-800">Contact Form</h3>
            <div className="mt-4 p-6 bg-gray-100 border border-dashed border-gray-300 rounded-lg text-center">
              <p className="text-gray-500">
                Our interactive contact form is currently under development. Please use the email address to the left to get in touch with us.
              </p>
              {/* TODO: Implement a real contact form here in the future */}
            </div>
          </div>
        </div>
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

export default ContactPage;