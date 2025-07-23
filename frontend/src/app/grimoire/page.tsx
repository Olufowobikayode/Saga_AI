// --- START OF FILE src/app/grimoire/page.tsx ---
import React from 'react';
import Link from 'next/link';
import { getAllScrolls, GrimoirePage } from '@/services/grimoireApi';

/**
 * The Grimoire Library Page: Displays all published scrolls of wisdom.
 * This is a Server Component, so it fetches data directly on the server.
 */
export default async function GrimoireLibraryPage() {
  const scrolls = await getAllScrolls();

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Page Header */}
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Saga Grimoire
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            A library of inscribed wisdom, complementing the Oracle's prophecies.
          </p>
        </header>

        {/* Grid of Grimoire Page Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {scrolls.length > 0 ? (
            scrolls.map((scroll) => (
              <Link href={`/grimoire/${scroll.slug}`} key={scroll.id}>
                <div className="bg-saga-surface p-6 rounded-lg border border-white/10 shadow-lg h-full
                                hover:border-saga-primary hover:scale-105 transition-all duration-300">
                  <h2 className="font-serif text-2xl font-bold text-saga-primary mb-3">
                    {scroll.title}
                  </h2>
                  <p className="text-saga-text-dark mb-4">
                    {scroll.summary}
                  </p>
                  <div className="text-sm text-saga-text-dark flex justify-between items-center">
                    <span>By {scroll.author}</span>
                    <span>{new Date(scroll.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            <div className="md:col-span-2 text-center text-saga-text-dark p-8 bg-saga-surface rounded-lg">
              <p>The Grimoire is currently empty. The Scribe has not yet inscribed any wisdom.</p>
            </div>
          )}
        </div>
        
        {/* Navigation Link to return to the Gateway */}
        <div className="text-center mt-16">
          <Link href="/" className="font-serif text-xl text-saga-text-dark hover:text-saga-primary transition-colors">
            ← Return to the Gateway
          </Link>
        </div>
      </div>
    </div>
  );
}
// --- END OF FILE src/app/grimoire/page.tsx ---