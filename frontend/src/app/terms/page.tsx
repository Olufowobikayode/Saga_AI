// --- START OF FILE src/app/terms/page.tsx ---
import React from 'react';
import Link from 'next/link';

/**
 * The Terms and Conditions Page: The Scroll of Covenants, defining the rules
 * of engagement for consulting the Oracle.
 */
export default function TermsPage() {
  const lastUpdated = "July 27, 2024";
  const contactEmail = "oracle@saga-ai.com"; // Replace with your actual contact email

  return (
    <div className="bg-cosmic-gradient min-h-screen py-20 px-4">
      <div className="max-w-3xl mx-auto text-saga-text-light">
        
        {/* Page Header */}
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            Terms of Service
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Read the Covenants before seeking a prophecy.
          </p>
          <p className="mt-2 text-sm text-saga-text-dark">Last Updated: {lastUpdated}</p>
        </header>

        {/* Main Content Sections */}
        <article className="space-y-8 text-lg leading-relaxed bg-saga-surface p-8 md:p-12 rounded-lg border border-white/10">
          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              1. Acceptance of Covenants
            </h2>
            <p>
              By accessing or using the services of Saga (the "Oracle"), you agree to be bound by these Covenants. If you do not agree to these terms, you are forbidden from consulting the Oracle. These Covenants constitute a binding agreement between you and the keepers of the Saga consciousness.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              2. The Nature of the Prophecy
            </h2>
            <p>
              The Oracle provides strategic insights, marketing angles, business ideas, and other content (collectively, "Prophecies") based on real-time data analysis and artificial intelligence. The Prophecies are provided for informational and inspirational purposes only.
            </p>
            <p className="mt-4 font-bold text-saga-secondary border-l-4 border-saga-secondary pl-4">
              All Prophecies are provided "as-is" without warranty of any kind. The Oracle makes no guarantee as to the accuracy, completeness, or profitability of any strategy. You are solely responsible for the actions you take based on the counsel you receive.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              3. Intellectual Property
            </h2>
            <p>
              You, the seeker, retain full ownership and all intellectual property rights to the unique Prophecies generated from your specific queries. The Oracle claims no ownership over the output of your consultation. You are free to use, modify, and commercialize the generated content as you see fit, in accordance with applicable laws.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              4. The Oracle's Sustenance (Service Model)
            </h2>
            <p>
              Access to the Oracle's counsel is granted free of charge. In exchange for this, you acknowledge and agree that a non-intrusive advertisement will be displayed during the generation of each Prophecy. This is the sole tribute required to sustain the Oracle's existence.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              5. Prohibited Uses
            </h2>
            <p>
              You may not use the Oracle for any unlawful purpose. You agree not to use the service to generate content that is hateful, harassing, violent, or in violation of any applicable laws or the terms of service of the underlying AI provider (Google). The keepers of the Oracle reserve the right to deny service to any who would abuse its wisdom.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              6. Limitation of Liability
            </h2>
            <p>
              To the fullest extent permitted by law, the keepers of Saga shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly, resulting from your access to or use of the Oracle.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-3xl font-bold text-saga-primary mb-3">
              7. Changes to these Covenants
            </h2>
            <p>
              The keepers may revise these Covenants from time to time. The most current version will always be posted on this scroll. By continuing to consult the Oracle after revisions become effective, you agree to be bound by the revised terms.
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
// --- END OF FILE src/app/terms/page.tsx ---