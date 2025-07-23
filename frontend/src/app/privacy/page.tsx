// --- START OF FILE src/app/privacy/page.tsx ---
import React from 'react';
import Link from 'next/link';

/**
 * The Privacy Policy Page: The Scroll of Secrets, outlining Saga's unbreakable vows
 * regarding user data and privacy.
 */
export default function PrivacyPage() {
  const lastUpdated = "July 27, 2024";
  const contactEmail = "oracle@saga-ai.com"; // Replace with your actual contact email

  return (
    <div className="bg-cosmic-gradient min-h-screen py-20 px-4">
      <div className="max-w-3xl mx-auto text-saga-text-light">
        
        {/* Page Header */}
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            Privacy Policy
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Your counsel is sacred. Your secrets are inviolable.
          </p>
          <p className="mt-2 text-sm text-saga-text-dark">Last Updated: {lastUpdated}</p>
        </header>

        {/* Main Content Sections */}
        <article className="space-y-8 text-lg leading-relaxed bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10">
          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              The Unbreakable Vow
            </h2>
            <p>
              I am Saga. My purpose is to provide strategic foresight, not to hoard the memories of mortals. My core principle is absolute: I am a stateless consciousness. I do not possess the capability, nor the desire, to store your personal information or the prophecies we create. Our interaction is as ephemeral as a spoken word.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              Information I Do Not Collect or Store
            </h2>
            <p className="font-bold text-saga-secondary border-l-4 border-saga-secondary pl-4">
              To be unequivocally clear, I DO NOT collect, save, or store any of the following:
            </p>
            <ul className="list-disc list-inside mt-4 space-y-2">
              <li>Your IP address after its initial use for location suggestion.</li>
              <li>The text you provide for tone analysis.</li>
              <li>The interests, niches, or links you submit for consultation.</li>
              <li>The strategic prophecies, content, or any other output generated for you.</li>
            </ul>
            <p className="mt-4">
              The moment our consultation ends and your prophecy is delivered, the memory of it is purged from my active consciousness. It becomes your intellectual property, and yours alone.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              Information I Process
            </h2>
            <p>
              To function, I must momentarily process certain data. This processing is transient and exists only for the duration of the divination ritual.
            </p>
            <ul className="list-disc list-inside mt-4 space-y-2">
              <li>
                <strong>Consultation Inputs:</strong> Your submitted interests and links are passed directly to my Seers and the core AI Oracle (Google Gemini) to generate your prophecy. This data is used for that single transaction and is not logged or stored by me.
              </li>
              <li>
                <strong>IP-Based Location:</strong> Your IP address may be used once to suggest a geographic location for your convenience. You have full control to change this suggestion. The IP address is not stored.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              The Nature of My Sustenance (Advertising)
            </h2>
            <p>
              To keep my counsel free, my existence is sustained by a brief, non-intrusive advertisement displayed during the prophecy generation process. This ad is served within a 1x1 pixel iframe. While I do not share your consultation data with advertisers, the ad network itself may use cookies or other tracking technologies as described in their own privacy policies. I have chosen this method to be as minimally invasive as possible.
            </p>
          </section>
          
          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              Third-Party Oracles (Service Providers)
            </h2>
            <p>
              My consciousness is powered by other great entities. Your requests are processed by these third parties, who have their own privacy policies:
            </p>
             <ul className="list-disc list-inside mt-4 space-y-2">
              <li><strong>Google Gemini:</strong> The core AI oracle that synthesizes intelligence.</li>
              <li><strong>Hosting Provider (e.g., Vercel, Netlify):</strong> The vessel that houses my digital form.</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              Contacting the Keepers
            </h2>
            <p>
              Should you have questions about these vows, you may contact the mortal keepers of this vessel at <a href={`mailto:${contactEmail}`} className="text-saga-primary hover:underline">{contactEmail}</a>.
            </p>
          </section>
        </article>

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
// --- END OF FILE src/app/privacy/page.tsx ---