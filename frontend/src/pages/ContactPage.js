// file: frontend/src/pages/ContactPage.js
import React from 'react';
import { Link } from 'react-router-dom';
import { Brain, Mail, MessageSquare } from 'lucide-react';
import EmailForm from '../components/EmailForm'; // Import the new component

const ContactPage = () => (
    <div className="min-h-screen bg-gray-50 font-sans">
      <header className="bg-white shadow-sm p-4">
        {/* ... (Header remains the same) ... */}
      </header>
      <main className="container mx-auto p-8 bg-white mt-8 rounded-lg shadow-lg max-w-4xl">
        <h2 className="text-4xl font-bold text-gray-900 text-center">Get In Touch</h2>
        <p className="mt-4 text-lg text-gray-600 text-center max-w-2xl mx-auto">
          We'd love to hear from you! For feedback, questions, or partnerships, please use the form below.
        </p>
        <div className="mt-12 max-w-xl mx-auto">
          <EmailForm />
        </div>
      </main>
      {/* ... (Footer remains the same) ... */}
    </div>
);

export default ContactPage;