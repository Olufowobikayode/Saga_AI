// --- START OF FILE src/app/page.tsx ---
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import CTASection from "@/components/CTASection"; // Summoning the CTA Section we just built.

export default function LandingPage() {
  return (
    <main className="overflow-x-hidden">
      {/* 
        The Landing Page is constructed from three thematic sections,
        creating a complete narrative for the user.
      */}
      
      {/* 1. The grand entrance to capture attention. */}
      <HeroSection />

      {/* 2. The scroll of power to explain the value. */}
      <FeaturesSection />

      {/* 3. The final command to drive action. */}
      <CTASection />

    </main>
  );
}
// --- END OF FILE src/app/page.tsx ---