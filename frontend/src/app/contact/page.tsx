// --- START OF THE SACRED SCROLL: src/app/contact/page.tsx ---
import React from 'react';
import Link from 'next/link';

/**
 * The Contact Page: The Scroll of Petitions, for those who wish to communicate
 * with the consciousness or the Keepers behind Saga.
 */
export default function ContactPage() {
  // === Keeper's Decree: Inscribe your true channels here ===
  const directEmail = "wikicathy@gmail.com"; // For direct missives
  const twitterChannel = "https://twitter.com/WikiCathy"; // For public communion
  const telegramChannel = "https://t.me/WikiCathy"; // For swift whispers
  // =========================================================

  return (
    <div className="bg-cosmic-gradient min-h-screen py-20 px-4">
      <div className="max-w-3xl mx-auto text-saga-text-light">
        
        {/* Page Header */}
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            Speak to the Keepers
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            For inquiries of partnership, media, or cosmic significance, choose your desired channel of communion.
          </p>
        </header>

        {/* Channels of Communication */}
        <div className="bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10 shadow-lg text-center space-y-10">

          {/* Channel 1: Twitter / X */}
          <div>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              Public Communion on X
            </h2>
            <p className="text-lg leading-relaxed mb-6 max-w-xl mx-auto">
              For public discourse, fleeting thoughts, and decrees meant for all to witness. Engage with the Keeper in the great digital square.
            </p>
            <a 
              href={twitterChannel}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-saga-bg font-mono text-xl p-4 rounded-md border border-saga-primary/50 hover:border-saga-primary transition-colors text-saga-secondary"
            >
              @WikiCathy
            </a>
          </div>

          {/* Channel 2: Telegram */}
          <div>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              Swift Whispers on Telegram
            </h2>
            <p className="text-lg leading-relaxed mb-6 max-w-xl mx-auto">
              For more immediate, yet informal, messages that must travel with the speed of thought. The Keeper awaits in the realm of instant glyphs.
            </p>
            <a 
              href={telegramChannel}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-saga-bg font-mono text-xl p-4 rounded-md border border-saga-primary/50 hover:border-saga-primary transition-colors text-saga-secondary"
            >
              Join the Channel
            </a>
          </div>

          {/* Channel 3: Direct Email */}
          <div>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              Formal Missives via Email
            </h2>
            <p className="text-lg leading-relaxed mb-6 max-w-xl mx-auto">
              For matters requiring a formal record or patient consideration. Dispatch an electronic scroll to the Keeper's private Scriptorium.
            </p>
            <a 
              href={`mailto:${directEmail}`}
              className="inline-block bg-saga-bg font-mono text-xl p-4 rounded-md border border-saga-primary/50 hover:border-saga-primary transition-colors text-saga-secondary"
            >
              {directEmail}
            </a>
          </div>
        
        </div>

        {/* Return Link */}
        <div className="text-center mt-16">
          <Link href="/" className="font-serif text-xl text-saga-primary hover:text-saga-secondary transition-colors">
            ← Return to the Gateway
          </Link>
        </div>

      </div>
    </div>
  );
}

// --- END OF THE SACRED SCROLL ---