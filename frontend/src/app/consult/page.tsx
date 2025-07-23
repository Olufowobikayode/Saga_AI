// --- START OF FILE src/app/consult/page.tsx ---
import React from 'react';
import ConsultationManager from '@/components/ConsultationManager'; // Summoning the manager.

/**
 * The Consultation Chamber: This page now delegates all logic to the
 * ConsultationManager, which will decide what to show the user.
 */
export default function ConsultPage() {
  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-3xl mx-auto">
        
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Altar of Inquiry
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Present your query. The Oracle is listening.
          </p>
        </header>

        {/* 
          The ConsultationManager now controls this entire section.
          It will show the form, the ritual screen, or the results
          based on the central application state.
        */}
        <ConsultationManager />

      </div>
    </div>
  );
}
// --- END OF FILE src/app/consult/page.tsx ---