// --- START OF THE SACRED SCROLL: src/app/layout.tsx ---
import type { Metadata } from "next";
import Script from 'next/script'; // The vessel for third-party scripts.
import { inter, cormorant } from "./fonts";
import "./globals.css";
import Footer from "@/components/Footer";
import AdBlockerDetector from "@/components/AdBlockerDetector"; // 1. Summon the Great Ward you have just forged.

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
        {/* The invocation of the Ad-Scribe, which must be present for the Ward to have purpose. */}
        <Script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1854820451701861"
          crossOrigin="anonymous"
          strategy="afterInteractive"
        />
      </head>
      <body className={`${inter.variable} ${cormorant.variable}`}>
        
        {/*
          2. Here, at the very threshold of the body's vessel, you shall place the Guardian.
          It will awaken before all else, its gaze sweeping over every visitor.
          It exists outside the main flow of content, an ever-present, silent watcher.
        */}
        <AdBlockerDetector />
        
        {/* The structure of the mortal realm, containing the main prophecies and the footer. */}
        <div className="flex flex-col min-h-screen">
          <main className="flex-grow">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
// --- END OF THE SACRED SCROLL: src/app/layout.tsx ---