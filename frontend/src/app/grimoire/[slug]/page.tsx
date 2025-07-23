// --- START OF FILE src/app/grimoire/[slug]/page.tsx ---
import React from 'react';
import Link from 'next/link';
import { getScrollBySlug } from '@/services/grimoireApi';
import { notFound } from 'next/navigation';

// SAGA LOGIC: Define the properties this page will receive.
// The 'slug' comes from the URL.
interface ScrollPageProps {
  params: {
    slug: string;
  };
}

/**
 * The Scroll Page: Displays the full content of a single Grimoire page.
 * This is a dynamic Server Component.
 */
export default async function ScrollPage({ params }: ScrollPageProps) {
  const { slug } = params;
  const scroll = await getScrollBySlug(slug);

  // If no scroll is found for the given slug, display a 404 page.
  if (!scroll) {
    notFound();
  }

  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-3xl mx-auto">
        
        {/* Page Header */}
        <header className="text-left mb-12">
          <h1 className="font-serif text-4xl md:text-6xl font-bold text-saga-secondary leading-tight">
            {scroll.title}
          </h1>
          <div className="mt-4 text-saga-text-dark flex items-center space-x-4">
            <span>By {scroll.author}</span>
            <span>•</span>
            <span>Inscribed on {new Date(scroll.created_at).toLocaleDateString()}</span>
          </div>
        </header>

        {/* The main article content, styled for maximum readability. */}
        <article 
          className="prose prose-lg prose-invert max-w-none 
                     prose-headings:font-serif prose-headings:text-saga-primary
                     prose-p:text-saga-text-light prose-p:leading-relaxed
                     prose-a:text-saga-primary hover:prose-a:text-saga-secondary
                     prose-strong:text-saga-text-light
                     prose-blockquote:border-l-saga-primary prose-blockquote:text-saga-text-dark"
          dangerouslySetInnerHTML={{ __html: scroll.content }}
        >
          {/* 
            'dangerouslySetInnerHTML' is used here to render HTML content from your database.
            This is safe as long as you trust the content you are putting into the database.
            For a public-facing blog where others might submit content, you would use a
            library like 'DOMPurify' to sanitize the HTML first. Since only you are the admin,
            this is secure.
          */}
        </article>
        
        {/* Navigation Link to return to the Library */}
        <div className="text-center mt-16 border-t border-white/10 pt-8">
          <Link href="/grimoire" className="font-serif text-xl text-saga-text-dark hover:text-saga-primary transition-colors">
            ← Return to the Grimoire Library
          </Link>
        </div>
      </div>
    </div>
  );
}
// --- END OF FILE src/app/grimoire/[slug]/page.tsx ---