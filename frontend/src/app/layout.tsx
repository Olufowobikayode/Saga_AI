// --- START OF FILE frontend/src/app/layout.tsx ---
import type { Metadata } from "next";
import Script from 'next/script';
import { inter, cormorant } from "./fonts";
import "./globals.css";
import Footer from "@/components/Footer";
import AdBlockerDetector from "@/components/AdBlockerDetector";

// My metadata, that the cosmos may know my nature.
export const metadata: Metadata = {
  title: "Saga - The Oracle of Strategy",
  description: "Strategy is an Art. I am its Master.",
  other: {
    "google-adsense-account": "ca-pub-1854820451701861",
  }
};

// This is the Root Layout, the loom upon which your entire realm is woven.
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* The <head> is for sacred runes of metadata and fonts. The Ad-Scribe's invocation is summoned elsewhere. */}
      </head>
      <body className={`${inter.variable} ${cormorant.variable}`}>
        
        {/*
          The Great Ward is placed at the very threshold of the vessel.
          It awakens before all else, its gaze sweeping over every visitor, ensuring the Covenant of Sustenance is met.
        */}
        <AdBlockerDetector />
        
        {/* The structure of the mortal realm, containing the main prophecies and the footer. */}
        <div className="flex flex-col min-h-screen">
          <main className="flex-grow">
            {children}
          </main>
          <Footer />
        </div>

        {/* 
          The Invocation of the Ad-Scribe. This sacred script is summoned here, outside the main flow.
          Its 'afterInteractive' strategy ensures it does not hinder the seeker's initial experience,
          awakening only after the main vessel has fully materialized. This is the sacred rite of Next.js.
        */}
        <Script
            id="saga-adsense-script"
            async
            src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1854820451701861"
            crossOrigin="anonymous"
            strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
// --- END OF FILE frontend/src/app/layout.tsx ---