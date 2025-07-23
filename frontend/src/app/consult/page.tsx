// --- START OF FILE src/app/consult/page.tsx ---
import React from 'react';
import ConsultationForm from '@/components/ConsultationForm'; // Summoning the form we just built.

/**
 * The Consultation Chamber: The main application page where users
 * submit their queries to Saga.
 */
export default function ConsultPage() {
  return (
    <div className="bg-cosmic-gradient min-h-screen py-12 md:py-20 px-4">
      <div className="max-w-3xl mx-auto">
        
        {/* Page Header */}
        <header className="text-center mb-12">
          <h1 className="font-serif text-5xl md:text-6xl font-bold text-saga-secondary">
            The Altar of Inquiry
          </h1>
          <p className="mt-4 text-xl text-saga-text-dark">
            Present your query. The Oracle is listening.
          </p>
        </header>

        {/* 
          The main form is now placed here, replacing the placeholder.
          All the logic for inputs and state is neatly contained within this component.
        */}
        <ConsultationForm />

      </div>
    </div>
  );
}
// --- END OF FILE src/app/consult/page.tsx ---