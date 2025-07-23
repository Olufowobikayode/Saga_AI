// --- START OF FILE src/components/Footer.tsx ---
import React from 'react';
import Link from 'next/link'; // Next.js component for optimized, client-side navigation.

/**
 * The Footer: The foundation of the temple, containing essential links and legal notices.
 */
export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-saga-surface border-t border-white/10 py-8 px-4">
      <div className="max-w-5xl mx-auto text-center text-saga-text-dark">
        
        {/* Navigation Links */}
        <div className="flex justify-center items-center space-x-6 mb-4">
          <Link href="/about" className="hover:text-saga-primary transition-colors">
            About Saga
          </Link>
          <Link href="/contact" className="hover:text-saga-primary transition-colors">
            Contact
          </Link>
          <Link href="/privacy" className="hover:text-saga-primary transition-colors">
            Privacy Policy
          </Link>
          <Link href="/terms" className="hover:text-saga-primary transition-colors">
            Terms of Service
          </Link>
        </div>

        {/* Core Message: Ad-supported and Privacy-focused */}
        <p className="mb-4 max-w-2xl mx-auto">
          Saga is a free service, sustained by non-intrusive advertising to cover the cosmic energies (server and API costs) required for each prophecy.
        </p>

        {/* Copyright Notice */}
        <p className="text-sm">
          © {currentYear} Saga. All rights reserved. Your strategies are your own.
        </p>
      </div>
    </footer>
  );
}
// --- END OF FILE src/components/Footer.tsx ---