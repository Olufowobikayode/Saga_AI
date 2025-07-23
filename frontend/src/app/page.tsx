// --- START OF FILE src/app/page.tsx ---
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection"; // Summoning the Features Section we just built.

export default function LandingPage() {
  return (
    <main className="overflow-x-hidden">
      {/* 
        The Landing Page is constructed from large, thematic sections.
        First, the grand entrance.
      */}
      <HeroSection />

      {/* 
        Second, as the user scrolls, the Scroll of Power is revealed.
      */}
      <FeaturesSection />

      {/* 
        In the future, we will add more sections below this one, such as:
        - A section showcasing the different prophecies.
        - A final call to action.
      */}
    </main>
  );
}
// --- END OF FILE src/app/page.tsx ---