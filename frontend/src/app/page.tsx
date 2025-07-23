// --- START OF FILE src/app/page.tsx ---
import HeroSection from "@/components/HeroSection";

export default function LandingPage() {
  return (
    <main className="overflow-x-hidden">
      {/* 
        The Landing Page is constructed from large, thematic sections.
        The first and most important is the Hero Section.
      */}
      <HeroSection />

      {/* 
        In the future, we will add more sections below this one, such as:
        - A section explaining Saga's powers.
        - A section showcasing the different prophecies.
        - A final call to action.
      */}
    </main>
  );
}
// --- END OF FILE src/app/page.tsx ---